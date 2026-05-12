"""Protocol defining the HTTP response interface used by pyssertive core assertions.

Any framework's response object that exposes the attributes below can be
wrapped in pyssertive's fluent assertion API. Django, httpx, werkzeug,
Starlette responses all match structurally — no adapter glue required at
the attribute level.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class HttpResponseProtocol(Protocol):
    """Structural interface required by core HTTP assertion mixins.

    Implementations must expose:

    * ``status_code`` — integer HTTP status.
    * ``content`` — raw response body as ``bytes``.
    * ``headers`` — case-insensitive mapping of response headers.
    * ``cookies`` — mapping of cookie name to a cookie object exposing
      ``.value`` (``str``) and ``dict``-style access for attributes like
      ``"max-age"``, ``"path"``. ``http.cookies.SimpleCookie`` satisfies
      this interface and is used internally by Django's ``HttpResponse``.
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
