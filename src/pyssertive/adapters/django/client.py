from __future__ import annotations

from typing import Any

from django.test import Client

from pyssertive.adapters.django.response import FluentResponse


class FluentHttpAssertClient:
    """
    Fluent wrapper for Django's test client.

    Example::

        client = FluentHttpAssertClient(Client())
        client.get('/api/').assert_ok().assert_json()
    """

    def __init__(self, base_client: Client) -> None:
        self._client: Client = base_client

    def get(self, *args: Any, **kwargs: Any) -> FluentResponse:
        response = self._client.get(*args, **kwargs)
        return FluentResponse(response)  # type: ignore[arg-type]

    def post(self, *args: Any, **kwargs: Any) -> FluentResponse:
        response = self._client.post(*args, **kwargs)
        return FluentResponse(response)  # type: ignore[arg-type]

    def put(self, *args: Any, **kwargs: Any) -> FluentResponse:
        response = self._client.put(*args, **kwargs)
        return FluentResponse(response)  # type: ignore[arg-type]

    def patch(self, *args: Any, **kwargs: Any) -> FluentResponse:
        response = self._client.patch(*args, **kwargs)
        return FluentResponse(response)  # type: ignore[arg-type]

    def delete(self, *args: Any, **kwargs: Any) -> FluentResponse:
        response = self._client.delete(*args, **kwargs)
        return FluentResponse(response)  # type: ignore[arg-type]

    def head(self, *args: Any, **kwargs: Any) -> FluentResponse:
        response = self._client.head(*args, **kwargs)
        return FluentResponse(response)  # type: ignore[arg-type]

    def options(self, *args: Any, **kwargs: Any) -> FluentResponse:
        response = self._client.options(*args, **kwargs)
        return FluentResponse(response)  # type: ignore[arg-type]

    def trace(self, *args: Any, **kwargs: Any) -> FluentResponse:
        response = self._client.trace(*args, **kwargs)
        return FluentResponse(response)  # type: ignore[arg-type]

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)
