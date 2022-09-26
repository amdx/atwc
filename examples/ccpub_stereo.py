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

import twc
import config


logger = logging.getLogger(__name__)


async def get_ccpub_meta(client, project_name):
    async with client.create_session():
        browser = twc.browsers.ModelBrowser(client)
        resource = await browser.load(project_name)

        logger.info(f'Resource: {resource["dcterms:title"]} '
                    f'ID: {resource["ID"]}')

        model = await browser.get_model_root()

        tagged_values = await browser.get_tagged_values(model, 'ccPublisher')
        logger.info(tagged_values)

        logger.info(f'Enabled: '
                    f'{tagged_values["serviceEnabled"][0].lower() == "true"}')

        scope_ids = twc.utils.extract_ids(tagged_values['scope'])
        scope_elements = await browser.get_elements_batch(scope_ids)

        scope_names = [await browser.get_qualified_name(scope['data'][1])
                       for scope in scope_elements.values()]
        logger.info(f'Scopes: {scope_names}')

        template_id = twc.utils.extract_ids(tagged_values['template'])[0]
        template_element = await browser.get_element(template_id)
        template_name = template_element['kerml:esiData']['name']

        logger.info(f'Template name: {template_name}')


async def main():
    client = twc.client.Client(config.URL, config.USER, config.PASSWORD)
    await get_ccpub_meta(client, 'TWCExploration')


if __name__ == '__main__':
    import asyncio

    logging.basicConfig(level=logging.INFO)

    asyncio.run(main())
