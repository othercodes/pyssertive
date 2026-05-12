from __future__ import annotations

from dataclasses import dataclass, field
from http.cookies import SimpleCookie
from typing import Any, ClassVar

from pyssertive.protocol import HttpResponseProtocol


@dataclass
class _CompleteResponse:
    status_code: int = 200
    content: bytes = b""
    headers: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, Any] = field(default_factory=dict)
    charset: str | None = "utf-8"


def test_protocol_should_accept_a_minimal_response_with_all_attributes():
    response = _CompleteResponse()

    assert isinstance(response, HttpResponseProtocol)


def test_protocol_should_accept_simple_cookie_as_cookies_mapping():
    cookies: SimpleCookie = SimpleCookie()
    cookies["session"] = "abc123"
    response = _CompleteResponse(cookies=cookies)

    assert isinstance(response, HttpResponseProtocol)


def test_protocol_should_reject_object_missing_required_attribute():
    class _MissingCharset:
        status_code: ClassVar[int] = 200
        content: ClassVar[bytes] = b""
        headers: ClassVar[dict[str, str]] = {}
        cookies: ClassVar[dict[str, Any]] = {}

    assert not isinstance(_MissingCharset(), HttpResponseProtocol)


def test_protocol_should_be_runtime_checkable_for_arbitrary_objects():
    assert not isinstance(object(), HttpResponseProtocol)
    assert not isinstance("not a response", HttpResponseProtocol)
    assert not isinstance(42, HttpResponseProtocol)
