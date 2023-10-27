import httpx
from httpx import Response


class CustomHTTPClient:
    TIMEOUT = 10

    def __init__(self, base_url, default_headers):
        self.base_url = base_url
        self.default_headers = default_headers
        self.client = httpx.Client(
            base_url=base_url,
            headers=default_headers,
            timeout=CustomHTTPClient.TIMEOUT
        )
        self.async_client = httpx.AsyncClient(
            base_url=base_url,
            headers=default_headers,
            timeout=CustomHTTPClient.TIMEOUT
        )

    def get(self, url, headers=None, params=None) -> Response:
        response = self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response

    async def async_get(self, url, headers=None, params=None) -> Response:
        response = await self.async_client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response

    async def post(self, url, headers=None, params=None, data=None) -> Response:
        response = self.client.post(url, headers=headers, params=params, data=data)
        response.raise_for_status()
        return response

    async def async_post(self, url, headers=None, params=None, data=None) -> Response:
        response = await self.async_client.post(url, headers=headers, params=params, data=data)
        response.raise_for_status()
        return response

