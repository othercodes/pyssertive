from __future__ import annotations

import json

import httpx
import pytest

from pyssertive.adapters.httpx import FluentHttpAssertClient, FluentResponse
from pyssertive.protocols.mcp import AssertableMCP


def _init_result() -> dict:
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "webshare", "version": "1.0.0"},
            "capabilities": {"tools": {}},
        },
    }


def _tool_call_result() -> dict:
    return {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {"content": [{"type": "text", "text": "72°C, partly cloudy"}]},
    }


def _make_response(body: dict, *, sse: bool = False) -> httpx.Response:
    if sse:
        content = f"event: message\ndata: {json.dumps(body)}\n\n".encode()
        headers = {"Content-Type": "text/event-stream"}
    else:
        content = json.dumps(body).encode()
        headers = {"Content-Type": "application/json"}
    request = httpx.Request("POST", "http://testserver/mcp")
    response = httpx.Response(200, content=content, headers=headers)
    response._request = request
    return response


def test_assert_mcp_should_return_assertable_when_no_callback_provided():
    fluent = FluentResponse(_make_response(_init_result()))
    result = fluent.assert_mcp()
    assert isinstance(result, AssertableMCP)
    result.negotiated_protocol("2024-11-05")


def test_assert_mcp_should_return_self_when_callback_provided():
    fluent = FluentResponse(_make_response(_init_result()))
    result = fluent.assert_mcp(lambda m: m.negotiated_protocol("2024-11-05").server_named("webshare"))
    assert result is fluent


def test_assert_mcp_should_parse_sse_response_transparently():
    fluent = FluentResponse(_make_response(_tool_call_result(), sse=True))
    fluent.assert_mcp(lambda m: m.tool("get_weather").returns_text_containing("°C"))


def test_assert_mcp_should_chain_with_http_assertions_via_client(monkeypatch: pytest.MonkeyPatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/mcp" and request.method == "POST":
            payload = json.loads(request.content)
            if payload.get("method") == "initialize":
                return _make_response(_init_result(), sse=True)
            return _make_response(_tool_call_result(), sse=True)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = FluentHttpAssertClient(httpx.Client(transport=transport, base_url="http://testserver"))

    client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
    ).assert_ok().assert_mcp(lambda m: m.negotiated_protocol("2024-11-05").server_named("webshare"))

    client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "get_weather", "arguments": {"location": "Madrid"}},
        },
    ).assert_ok().assert_mcp(lambda m: m.tool("get_weather").succeeds().returns_text_containing("°C"))
