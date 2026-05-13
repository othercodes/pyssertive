from __future__ import annotations

from typing import Any

import httpx

from pyssertive.adapters.httpx.response import FluentResponse


class FluentHttpAssertClient:
    def __init__(self, base_client: httpx.Client) -> None:
        self._client: httpx.Client = base_client

    def get(self, *args: Any, **kwargs: Any) -> FluentResponse:
        return FluentResponse(self._client.get(*args, **kwargs))

    def post(self, *args: Any, **kwargs: Any) -> FluentResponse:
        return FluentResponse(self._client.post(*args, **kwargs))

    def put(self, *args: Any, **kwargs: Any) -> FluentResponse:
        return FluentResponse(self._client.put(*args, **kwargs))

    def patch(self, *args: Any, **kwargs: Any) -> FluentResponse:
        return FluentResponse(self._client.patch(*args, **kwargs))

    def delete(self, *args: Any, **kwargs: Any) -> FluentResponse:
        return FluentResponse(self._client.delete(*args, **kwargs))

    def head(self, *args: Any, **kwargs: Any) -> FluentResponse:
        return FluentResponse(self._client.head(*args, **kwargs))

    def options(self, *args: Any, **kwargs: Any) -> FluentResponse:
        return FluentResponse(self._client.options(*args, **kwargs))

    def request(self, method: str, *args: Any, **kwargs: Any) -> FluentResponse:
        return FluentResponse(self._client.request(method, *args, **kwargs))

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)
