from __future__ import annotations

import httpx

from pyssertive.adapters.httpx import FluentResponse


def _make_response(**kwargs) -> httpx.Response:
    request = httpx.Request("GET", "http://testserver/x")
    response = httpx.Response(**kwargs)
    response._request = request
    return response


def test_fluent_response_should_expose_charset_from_httpx_charset_encoding():
    raw = _make_response(status_code=200, content=b"data", headers={"Content-Type": "text/plain; charset=utf-16"})
    assert FluentResponse(raw).charset == "utf-16"


def test_fluent_response_should_return_none_charset_when_response_has_no_charset():
    raw = _make_response(status_code=200, content=b"data", headers={"Content-Type": "application/octet-stream"})
    assert FluentResponse(raw).charset is None


def test_fluent_response_should_forward_httpx_specific_attribute():
    raw = _make_response(status_code=200, content=b"hi")
    assert FluentResponse(raw).text == "hi"
