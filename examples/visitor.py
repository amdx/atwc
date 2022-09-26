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

"""
Demonstrate how to use ModelBrowser to recursively visit the model

$ python visitor.py <project_name>
"""

import sys
import logging

import twc
import config


logger = logging.getLogger(__name__)


async def print_children(element, browser, level=0):
    if element["kerml:ownedElement"]:
        owned_elements_ids = twc.utils.extract_ids(
            element["kerml:ownedElement"]
        )
        queried_elements = await browser.get_elements_batch(owned_elements_ids)
        owned_elements = [
            el['data'][1] for el in queried_elements.values()
            if el['status'] == 200
        ]

        for child in owned_elements:
            name = child['kerml:esiData'].get('name', 'N/A')
            print('-' * level, f' name={name} type={child["@type"]} '
                               f'id={child["@id"]}')

            await print_children(child, browser, level + 1)


async def main(project_name):
    client = twc.client.Client(config.URL, config.USER, config.PASSWORD)

    async with client.create_session():
        browser = twc.browsers.ModelBrowser(client=client)
        await browser.load(project_name)

        root = await browser.get_model_root()
        print(f'Model root package: id={root["kerml:esiData"]["ID"]} '
              f'name={root["kerml:esiData"]["name"]}')

        await print_children(root, browser)


if __name__ == '__main__':
    import asyncio

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) != 2:
        logger.error(f'Usage: {sys.argv[0]} <project_name>')
        sys.exit(1)

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )
    asyncio.run(main(sys.argv[1]))
