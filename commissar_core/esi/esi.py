import asyncio

import cachetools
import httpx

from commissar_core import SingletonMeta
from commissar_core.esi.http_client import CustomHTTPClient
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception

from commissar_core.log import LOGGER


class RetryStrategy(retry_if_exception):
    """Retry strategy that retries if the exception is an ``HTTPStatusError`` with
    specified status codes.

    """

    def __init__(self):
        def is_retryable(exception):
            return (
                isinstance(exception, httpx.HTTPStatusError) and
                exception.response.status_code in (408, 429, 502, 503, 504)
            )
        super().__init__(predicate=is_retryable)


class ESI(CustomHTTPClient, metaclass=SingletonMeta):
    USER_AGENT = 'EVECommissar'
    BASE_URL = 'https://esi.evetech.net/latest'
    RETRIES = 2
    DELAY = 0.5

    def __init__(self):
        self.base_url = ESI.BASE_URL
        self.default_headers = {
            "Accept": "application/json",
            "Cache-Control": "no-cache",
            'User-Agent': self.USER_AGENT
        }
        self.default_parameters = {'datasource': 'tranquility', 'language': 'en'}
        super().__init__(self.base_url, self.default_headers)

    # -----------------------------------------------------------------------------------------------------------------
    # curl - X GET "https://esi.evetech.net/latest/characters/1/?datasource=tranquility"
    # - H "accept: application/json"
    # - H "Cache-Control: no-cache"
    @retry(retry=RetryStrategy(), stop=stop_after_attempt(RETRIES), wait=wait_fixed(DELAY))
    @cachetools.cached(cache=cachetools.TTLCache(maxsize=10, ttl=900))
    def get_character(self, character_id):
        data = None
        try:
            url = "".join(['/characters/', str(character_id), '/'])
            response = self.get(url, params=self.default_parameters)
            if response.status_code == 200:
                data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pass
        return data

    async def async_get_character(self, character_id):
        data = None
        try:
            url = "".join(['/characters/', str(character_id), '/'])
            response = await self.async_get(url, params=self.default_parameters)
            if response.status_code == 200:
                data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pass
        return character_id
        yield data

    async def async_get_characters_corp(self, characters_ids: list[int]):
        results = []
        tasks = []
        for characters_id in characters_ids:
            task = asyncio.create_task(self.async_get_character(characters_id))
            tasks.append(task)
        gather_data = []
        try:
            gather_data = await asyncio.gather(*tasks)
        except Exception as e:
            LOGGER.error(e, exc_info=True)
            pass
        for character_id, data in gather_data:
            _t = (character_id, data['corporation_id'], data['alliance_id'])
            results.append(_t)
        return results

    # -----------------------------------------------------------------------------------------------------------------
    # curl - X GET "https://esi.evetech.net/latest/corporations/1/?datasource=tranquility"
    # - H "accept: application/json"
    # - H "Cache-Control: no-cache"
    @retry(retry=RetryStrategy(), stop=stop_after_attempt(RETRIES), wait=wait_fixed(DELAY))
    @cachetools.cached(cache=cachetools.TTLCache(maxsize=10, ttl=900))
    def get_corporation(self, corporation_id):
        data = None
        try:
            url = "".join(['/corporations/', str(corporation_id)])
            response = self.get(url, params=self.default_parameters)
            if response.status_code == 200:
                data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pass
        return data

    @cachetools.cached(cache=cachetools.TTLCache(maxsize=10, ttl=900))
    async def async_get_corporation(self, corporation_id):
        data = None
        try:
            url = "".join(['/corporations/', str(corporation_id)])
            response = await self.async_get(url, params=self.default_parameters)
            if response.status_code == 200:
                data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pass
        return data

    # -----------------------------------------------------------------------------------------------------------------
    # curl - X GET "https://esi.evetech.net/latest/alliances/1/?datasource=tranquility"
    # - H "accept: application/json"
    # - H "Cache-Control: no-cache"
    @retry(retry=RetryStrategy(), stop=stop_after_attempt(RETRIES), wait=wait_fixed(DELAY))
    @cachetools.cached(cache=cachetools.TTLCache(maxsize=10, ttl=900))
    def get_alliance(self, alliance_id):
        data = None
        try:
            url = "".join(['/alliances/', str(alliance_id)])
            response = self.get(url, params=self.default_parameters)
            if response.status_code == 200:
                data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pass
        return data

    @cachetools.cached(cache=cachetools.TTLCache(maxsize=10, ttl=900))
    async def async_get_alliance(self, alliance_id):
        data = None
        try:
            url = "".join(['/alliances/', str(alliance_id)])
            response = await self.async_get(url, params=self.default_parameters)
            if response.status_code == 200:
                data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pass
        return data

