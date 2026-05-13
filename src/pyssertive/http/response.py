from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, cast, runtime_checkable

from pyssertive.http.assertions import (
    CookieAssertionsMixin,
    HeaderAssertionsMixin,
    HttpStatusAssertionsMixin,
)
from pyssertive.http.debug import DebugResponseMixin
from pyssertive.http.html import HTMLContentAssertionsMixin
from pyssertive.http.json import JsonContentAssertionsMixin


@runtime_checkable
class ResponseProtocol(Protocol):
    """Public contract exposed by every pyssertive ``FluentResponse``.

    Describes the common surface area of an HTTP response — the data
    accessors that all framework adapters guarantee regardless of the
    underlying response type. Type your cross-framework helpers against
    this protocol and they will accept any ``FluentResponse`` (Django,
    httpx, etc.) interchangeably::

        def my_check(response: ResponseProtocol) -> None:
            assert response.status_code == 200
            assert json.loads(response.content)["ok"] is True

    Members:

    * ``status_code`` — integer HTTP status.
    * ``content`` — raw response body as ``bytes``.
    * ``headers`` — case-insensitive mapping of response headers.
    * ``cookies`` — mapping of cookie name to a cookie object exposing
      ``.value`` (``str``) and ``dict``-style access for attributes like
      ``"max-age"``, ``"path"``. ``http.cookies.SimpleCookie`` satisfies
      this interface.
    * ``charset`` — optional character set declared by the response.
    """

    @property
    def status_code(self) -> int: ...  # pragma: no cover

    @property
    def content(self) -> bytes: ...  # pragma: no cover

    @property
    def headers(self) -> Mapping[str, str]: ...  # pragma: no cover

    @property
    def cookies(self) -> Mapping[str, Any]: ...  # pragma: no cover

    @property
    def charset(self) -> str | None: ...  # pragma: no cover


class FluentResponse(
    DebugResponseMixin,
    CookieAssertionsMixin,
    HTMLContentAssertionsMixin,
    JsonContentAssertionsMixin,
    HeaderAssertionsMixin,
    HttpStatusAssertionsMixin,
):
    """Framework-agnostic fluent assertion wrapper for HTTP responses.

    Concrete adapter subclasses (e.g. ``pyssertive.adapters.django.FluentResponse``
    or ``pyssertive.adapters.httpx.FluentResponse``) define their own
    ``__init__`` with the framework-native response type and override
    properties when the underlying response shape diverges (e.g. httpx
    exposes ``charset_encoding`` instead of ``charset``).

    Every concrete FluentResponse satisfies :class:`ResponseProtocol`,
    so developers can write helpers typed against that protocol and have
    them work uniformly across adapters.
    """

    _response: Any

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def wrapped(self) -> Any:
        return self._response

    @property
    def status_code(self) -> int:  # type: ignore[override]
        return cast(int, self._response.status_code)

    @property
    def content(self) -> bytes:  # type: ignore[override]
        return cast(bytes, self._response.content)

    @property
    def headers(self) -> Any:
        return self._response.headers

    @property
    def cookies(self) -> Any:
        return self._response.cookies

    @property
    def charset(self) -> str | None:
        return cast("str | None", self._response.charset)
