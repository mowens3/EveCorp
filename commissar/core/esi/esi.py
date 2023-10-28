import functools

import aiometer
from async_lru import alru_cache
import httpx

from commissar import SingletonMeta
from commissar.core.esi.http_client import CustomHTTPClient
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception

from commissar import LOGGER


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
        self.counter = 0
        super().__init__(self.base_url, self.default_headers)

    # -----------------------------------------------------------------------------------------------------------------
    # curl - X GET "https://esi.evetech.net/latest/characters/1/?datasource=tranquility"
    # - H "accept: application/json"
    # - H "Cache-Control: no-cache"
    @retry(retry=RetryStrategy(), stop=stop_after_attempt(RETRIES), wait=wait_fixed(DELAY))
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
        finally:
            self.counter += 1
        return data

    @alru_cache(maxsize=500, ttl=15 * 60)
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
        finally:
            self.counter += 1
        return character_id, data

    async def async_get_characters(self, characters_ids: list[int]):
        results = []
        try:
            tasks = [
                functools.partial(self.async_get_character, characters_id) for characters_id in characters_ids
            ]
            results = await aiometer.run_all(tasks, max_at_once=2, max_per_second=5)
        except Exception as e:
            LOGGER.error(e, exc_info=True)
        return results

    # -----------------------------------------------------------------------------------------------------------------
    # curl - X GET "https://esi.evetech.net/latest/corporations/1/?datasource=tranquility"
    # - H "accept: application/json"
    # - H "Cache-Control: no-cache"
    @retry(retry=RetryStrategy(), stop=stop_after_attempt(RETRIES), wait=wait_fixed(DELAY))
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
        finally:
            self.counter += 1
        return data

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
        finally:
            self.counter += 1
        return data

    # -----------------------------------------------------------------------------------------------------------------
    # curl - X GET "https://esi.evetech.net/latest/alliances/1/?datasource=tranquility"
    # - H "accept: application/json"
    # - H "Cache-Control: no-cache"
    @retry(retry=RetryStrategy(), stop=stop_after_attempt(RETRIES), wait=wait_fixed(DELAY))
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
        finally:
            self.counter += 1
        return data

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
        finally:
            self.counter += 1
        return data

