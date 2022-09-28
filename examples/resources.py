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
Print a list of all resources available from the server

$ python resources.py
"""

import logging

import atwc
import config


logger = logging.getLogger(__name__)


async def list_resources(client):
    async with client.create_session():
        browser = atwc.browsers.ResourceBrowser(client)
        await browser.fetch()

        logger.info('CC resources:')
        for resource in browser.cc_resources:
            logger.info(f'  {resource["dcterms:title"]}')

        logger.info('MD resources:')
        for resource in browser.md_resources:
            logger.info(f'  {await browser.get_category_path(resource)}/'
                        f'{resource["dcterms:title"]}')


async def main():
    client = atwc.client.Client(config.URL, config.USER, config.PASSWORD)
    await list_resources(client)


if __name__ == '__main__':
    import asyncio

    logging.basicConfig(level=logging.INFO)

    asyncio.run(main())
