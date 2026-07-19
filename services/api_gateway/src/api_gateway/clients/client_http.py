from typing import Any

import httpx

from api_gateway.core.core_config import settings


class HTTPClient:
    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        if self._client is not None:
            return

        timeout = httpx.Timeout(
            connect=settings.HTTP_CONNECT_TIMEOUT,
            read=settings.HTTP_READ_TIMEOUT,
            write=settings.HTTP_READ_TIMEOUT,
            pool=settings.HTTP_CONNECT_TIMEOUT,
        )

        limits = httpx.Limits(
            max_connections=200,
            max_keepalive_connections=50,
        )

        self._client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            follow_redirects=False,
        )

        print("[API Gateway HTTP] Client started")

    async def stop(self) -> None:
        if self._client is None:
            return

        await self._client.aclose()
        self._client = None

        print("[API Gateway HTTP] Client stopped")

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("HTTP client is not started")

        return self._client

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: Any = None,
        content: bytes | None = None,
    ) -> httpx.Response:
        return await self.client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            content=content,
        )


http_client = HTTPClient()