from __future__ import annotations

import json
from collections.abc import Callable
from http.cookies import SimpleCookie
from typing import Any

import httpx
import pytest
from django.http import HttpRequest, HttpResponse

from pyssertive.adapters.django import DjangoRequestBuilder
from pyssertive.adapters.django.response import FluentResponse as DjangoFluentResponse
from pyssertive.adapters.httpx import HttpxRequestBuilder
from pyssertive.adapters.httpx.response import FluentResponse as HttpxFluentResponse


def _pair(django_fn: Callable[..., Any], httpx_fn: Callable[..., Any]) -> list[Any]:
    return [pytest.param(django_fn, id="django"), pytest.param(httpx_fn, id="httpx")]


def inspect(built: Any) -> dict[str, Any]:
    match built:
        case HttpRequest():
            return {
                "method": built.method or "",
                "path": built.path,
                "headers": {k.lower(): v for k, v in built.headers.items()},
                "cookies": dict(built.COOKIES),
                "query": {k: built.GET[k] for k in built.GET},
                "body": built.body if built.method in ("POST", "PUT", "PATCH") else None,
            }
        case httpx.Request():
            headers = {k.lower(): v for k, v in built.headers.items()}
            cookies = SimpleCookie()
            cookies.load(headers.get("cookie", ""))
            return {
                "method": built.method,
                "path": built.url.path,
                "headers": headers,
                "cookies": {k: m.value for k, m in cookies.items()},
                "query": {k: v for k, v in built.url.params.items()},
                "body": built.content,
            }
        case _:
            raise TypeError(f"Unknown built type: {type(built).__name__}")


REQUEST_BUILDER_ADAPTERS = _pair(
    lambda: DjangoRequestBuilder(base_url="http://test"),
    lambda: HttpxRequestBuilder(base_url="http://test"),
)


def _make_django_response(
    body: Any = b"",
    *,
    status: int = 200,
    content_type: str | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, dict[str, Any]] | None = None,
) -> DjangoFluentResponse:
    raw = body if isinstance(body, (str, bytes)) else json.dumps(body)
    kwargs: dict[str, Any] = {"status": status, "headers": headers or {}}
    if content_type:
        kwargs["content_type"] = content_type
    response = HttpResponse(raw, **kwargs)
    if cookies:
        for name, opts in cookies.items():
            response.set_cookie(name, **opts)
    return DjangoFluentResponse(response)


def _make_httpx_response(
    body: Any = b"",
    *,
    status: int = 200,
    content_type: str | None = None,
    headers: dict[str, str] | None = None,
    cookies: dict[str, dict[str, Any]] | None = None,
) -> HttpxFluentResponse:
    raw_headers: list[tuple[str, str]] = [(k, v) for k, v in (headers or {}).items()]
    if content_type:
        raw_headers.append(("Content-Type", content_type))
    if cookies:
        for name, opts in cookies.items():
            value = opts.get("value", "")
            parts = [f"{name}={value}", "Path=" + opts.get("path", "/")]
            if "max_age" in opts:
                parts.append(f"Max-Age={opts['max_age']}")
            raw_headers.append(("Set-Cookie", "; ".join(parts)))

    if isinstance(body, str):
        content = body.encode()
    elif isinstance(body, (bytes, bytearray)):
        content = bytes(body)
    else:
        content = json.dumps(body).encode()

    response = httpx.Response(status, content=content, headers=raw_headers)
    response._request = httpx.Request("GET", "http://test/")
    return HttpxFluentResponse(response)


RESPONSE_FACTORIES = _pair(_make_django_response, _make_httpx_response)
