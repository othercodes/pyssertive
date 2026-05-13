from __future__ import annotations

import json

import httpx
import pytest

from pyssertive.adapters.httpx import FluentHttpAssertClient


def _handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/json/":
        return httpx.Response(
            200,
            json={"ok": True, "method": request.method},
            headers={"X-Echo-Method": request.method},
        )
    if path == "/created/":
        return httpx.Response(201, json={"id": 1})
    if path == "/redirect/":
        return httpx.Response(302, headers={"Location": "/target/"})
    if path == "/sse/":
        body = 'event: message\ndata: {"jsonrpc": "2.0", "id": 1, "result": {"value": 42}}\n\n'
        return httpx.Response(
            200,
            content=body.encode("utf-8"),
            headers={"Content-Type": "text/event-stream"},
        )
    if path == "/cookies/":
        response = httpx.Response(200, json={})
        response.headers["Set-Cookie"] = "session=abc; Path=/"
        return response
    if path == "/echo-body/":
        return httpx.Response(200, content=request.content, headers=dict(request.headers))
    return httpx.Response(404, json={"detail": "not found"})


@pytest.fixture
def fluent_client() -> FluentHttpAssertClient:
    transport = httpx.MockTransport(_handler)
    return FluentHttpAssertClient(httpx.Client(transport=transport, base_url="http://testserver"))


@pytest.fixture
def fluent_client_with_body_echo() -> FluentHttpAssertClient:
    def echo(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=request.content or json.dumps({"empty": True}).encode("utf-8"),
            headers={"Content-Type": request.headers.get("content-type", "application/json")},
        )

    transport = httpx.MockTransport(echo)
    return FluentHttpAssertClient(httpx.Client(transport=transport, base_url="http://testserver"))
