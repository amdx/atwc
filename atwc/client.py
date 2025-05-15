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
import time
import urllib.parse
from contextlib import asynccontextmanager
import json

import aiohttp

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, api_url, login, password):
        assert api_url
        if api_url[-1] != '/':
            api_url += '/'

        self._api_url = api_url
        self._auth = aiohttp.BasicAuth(login=login, password=password)
        self._session = None

    @asynccontextmanager
    async def create_session(self):
        jar = aiohttp.CookieJar(unsafe=True)
        tstart = time.time()
        async with aiohttp.ClientSession(
                auth=self._auth,
                raise_for_status=True,
                cookie_jar=jar
        ) as self._session:
            logger.debug('Session opened')
            await self._login()
            try:
                yield self._session
            finally:
                await self._logout()
                self._session = None
                logger.debug(f'Session closed, total time: '
                             f'{time.time() - tstart}s')

    async def get(self, path):
        assert self._session
        url = urllib.parse.urljoin(self._api_url, path)
        logger.debug(f'Querying {url}')
        async with self._session.get(url) as response:
            payload = await response.json()
            status = response.status

        return status, payload

    async def post(self, path, data):
        assert self._session
        url = urllib.parse.urljoin(self._api_url, path)
        logger.debug(f'Posting to {url} data={data}')

        if type(data) != str:
            data = json.dumps(data)

        async with self._session.post(url, data=data) as response:
            payload = await response.json()
            status = response.status

        return status, payload

    async def _login(self):
        status, payload = await self.get('login')
        if status != 204:
            raise ConnectionError('Cannot login to TWC')
        else:
            logger.debug(f'Logged in as {self._auth.login}')

    async def _logout(self):
        status, payload = await self.get('logout')
        if status != 204:
            raise ConnectionError('Cannot logout from TWC')
        else:
            logger.debug('Logged out')
