from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from pyssertive.http.response import FluentResponse


@dataclass
class _FakeResponse:
    status_code: int = 200
    content: bytes = b""
    headers: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, Any] = field(default_factory=dict)
    charset: str | None = "utf-8"
    extra: str = "framework-specific-attribute"


def test_core_fluent_response_should_wrap_any_protocol_compatible_response():
    fake = _FakeResponse(status_code=201, content=b'{"ok": true}', headers={"Content-Type": "application/json"})
    response = FluentResponse(fake)

    response.assert_created().assert_content_type("application/json").assert_json_path("ok", True)


def test_core_fluent_response_should_expose_wrapped_response():
    fake = _FakeResponse()
    response = FluentResponse(fake)

    assert response.wrapped is fake


def test_core_fluent_response_should_proxy_protocol_properties():
    fake = _FakeResponse(status_code=418, content=b"teapot", charset="ascii")
    response = FluentResponse(fake)

    assert response.status_code == 418
    assert response.content == b"teapot"
    assert response.charset == "ascii"
    assert response.headers == {}
    assert response.cookies == {}


def test_core_fluent_response_should_forward_unknown_attributes_to_wrapped_response():
    fake = _FakeResponse()
    response = FluentResponse(fake)

    assert response.extra == "framework-specific-attribute"


def test_core_fluent_response_should_raise_attribute_error_for_truly_unknown_attribute():
    fake = _FakeResponse()
    response = FluentResponse(fake)

    with pytest.raises(AttributeError):
        _ = response.this_does_not_exist_anywhere
