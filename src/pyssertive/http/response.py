from __future__ import annotations

from typing import Any

from pyssertive.http.assertions import (
    CookieAssertionsMixin,
    HeaderAssertionsMixin,
    HttpStatusAssertionsMixin,
)
from pyssertive.http.debug import DebugResponseMixin
from pyssertive.http.html import HTMLContentAssertionsMixin
from pyssertive.http.json import JsonContentAssertionsMixin
from pyssertive.protocol import HttpResponseProtocol


class FluentResponse(
    DebugResponseMixin,
    CookieAssertionsMixin,
    HTMLContentAssertionsMixin,
    JsonContentAssertionsMixin,
    HeaderAssertionsMixin,
    HttpStatusAssertionsMixin,
):
    """Framework-agnostic fluent assertion wrapper for HTTP responses.

    Wraps any object that satisfies :class:`HttpResponseProtocol` and
    exposes the core assertion families (status, header, cookie, JSON,
    HTML, debug). Adapter packages extend this with framework-specific
    mixins (e.g. ``pyssertive.adapters.django`` adds template, form,
    session, and streaming assertions).
    """

    def __init__(self, response: HttpResponseProtocol) -> None:
        self._response: HttpResponseProtocol = response

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def wrapped(self) -> HttpResponseProtocol:
        return self._response

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def content(self) -> bytes:
        return self._response.content

    @property
    def headers(self) -> Any:
        return self._response.headers

    @property
    def cookies(self) -> Any:
        return self._response.cookies

    @property
    def charset(self) -> str | None:
        return self._response.charset
