#   Copyright 2022 Archimedes Exhibitions GmbH
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging

from atwc import utils


logger = logging.getLogger(__name__)


class ResourceBrowser:
    def __init__(self, client):
        self._client = client
        self._resources = []

    @property
    def cc_resources(self):
        return [r for r in self._resources
                if r['dcterms:title'][-3:] == '.CC']

    @property
    def md_resources(self):
        return [r for r in self._resources
                if r['dcterms:title'][-7:] == '.MASTER']

    @property
    def all_resources(self):
        return self._resources

    async def fetch(self):
        status, self._resources = await self._client.get(
            'resources?includeBody=true'
        )
        logger.debug(f'Loaded {len(self._resources)} resources')

    async def get_category_sequence(self, resource):
        hops = []
        category_id = resource['categoryID']

        while True:
            status, category = await self._client.get(
                f'workspaces/{category_id}/resources'
            )
            hops.append(category[1]['dcterms:title'])
            category_id = category[1]['kerml:parentID']

            if not category_id:
                break

        return hops[::-1]

    async def get_category_path(self, resource):
        return '/'.join(await self.get_category_sequence(resource))


class ModelBrowser:
    def __init__(self, client, resource=None):
        self._client = client
        self._resource = resource

    async def load(self, resource_name, suffix='MASTER'):
        logger.debug(f'Finding resource {resource_name} suffix={suffix}')
        status, resources = await self._client.get(
            'resources?includeBody=true'
        )
        for resource in resources:
            if resource['dcterms:title'] == f'{resource_name}.{suffix}':
                self._resource = resource
                return resource

        raise RuntimeError(f'Cannot find resource {resource_name}.{suffix}')

    async def get_revision_info(self, revision=None):
        assert self._resource
        if revision is None:
            status, revs = await self._client.get(
                f'resources/{self._resource["ID"]}/revisions'
            )
            revision = revs[0]

        logger.debug(f'Fetching info for revision {revision}')

        status, revdata = await self._client.get(
            f'resources/{self._resource["ID"]}/revisions/{revision}'
        )
        # Note: this fixes the missing ID of the revision from the payload
        revdata[0]["ID"] = revision

        return revdata[0]

    async def get_element(self, element_id):
        assert self._resource
        status, result = await self._client.get(
            f'resources/{self._resource["ID"]}/elements/{element_id}',
        )

        # What's on idx=0?
        return result[1]

    async def get_elements_batch(self, elements_id):
        assert self._resource
        assert isinstance(elements_id, list) \
               or isinstance(elements_id, tuple) \
               or isinstance(elements_id, set)

        status, result = await self._client.post(
            f'resources/{self._resource["ID"]}/elements',
            data=list(elements_id)
        )

        return result

    async def get_model_root(self):
        revdata = await self.get_revision_info()
        project_id = revdata['rootObjectIDs'][0]
        project = await self.get_element(project_id)

        owned_sections_ids = [a['@id']
                              for a in
                              project['kerml:esiData']['ownedSections']]

        owned_sections = await self.get_elements_batch(owned_sections_ids)

        for uuid, element in owned_sections.items():
            esi_data = element['data'][1]['kerml:esiData']
            if esi_data['name'] == 'model':
                model_id = esi_data['rootElements'][0]
                return await self.get_element(model_id)

        return None

    async def find_stereotype(self, element, name):
        stereo_ids = utils.extract_ids(
            element['kerml:esiData']['appliedStereotype']
        )
        if not stereo_ids:
            return None

        stereos = await self.get_elements_batch(stereo_ids)
        for stereo_id, stereo in stereos.items():
            data = stereo['data'][1]
            if data['kerml:esiData']['name'] == name:
                return data

        return None

    async def get_tagged_values(self, element, stereotype_name=None):
        tagged_values_kv = {}

        if stereotype_name:
            ccp_stereo = await self.find_stereotype(element, stereotype_name)
            if ccp_stereo is None:
                logger.debug(f'No applied stereotype {stereotype_name}')
                return None
            ccp_stereo_id = ccp_stereo["kerml:esiID"]
        else:
            ccp_stereo_id = None

        tagged_value_ids = utils.extract_ids(
            element['kerml:esiData']['taggedValue']
        )
        tagged_values = await self.get_elements_batch(tagged_value_ids)

        for tv_id, tagged_value in tagged_values.items():
            data = tagged_value['data'][1]['kerml:esiData']
            tv_def_id = utils.extract_ids(data['tagDefinition'])[0]

            tv_def = await self.get_element(tv_def_id)
            tv_def_name = tv_def['kerml:esiData']['name']

            if ccp_stereo_id is not None:
                tv_def_owner_id = utils.extract_ids(tv_def['kerml:owner'])[0]
                if tv_def_owner_id != ccp_stereo_id:
                    logger.debug(f'Skipping tagged value id={tv_id} '
                                 f'since it is not owned by '
                                 f'stereotype {stereotype_name}')
                    continue

            tagged_values_kv[tv_def_name] = data['value']

        return tagged_values_kv

    async def get_all_ancestors(self, element):
        ancestors = []

        node = element
        while True:
            owning_package = node['kerml:esiData']['owningPackage']
            if owning_package is None:
                break

            owning_package_id = utils.extract_ids(owning_package)[0]
            node = await self.get_element(owning_package_id)
            ancestors.append(node)

        return ancestors

    async def get_qualified_name(self, element):
        ancestors = (await self.get_all_ancestors(element))[-2::-1]
        names = [el['kerml:esiData']['name'] for el in ancestors + [element]]

        return '::'.join(names)
