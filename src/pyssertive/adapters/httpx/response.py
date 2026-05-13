from __future__ import annotations

from http.cookies import SimpleCookie

import httpx

from pyssertive.http.mcp import MCPAssertionsMixin
from pyssertive.http.response import FluentResponse as _BaseFluentResponse


class FluentResponse(MCPAssertionsMixin, _BaseFluentResponse):
    def __init__(self, response: httpx.Response) -> None:
        self._response: httpx.Response = response

    @property
    def charset(self) -> str | None:
        return self._response.charset_encoding

    @property
    def cookies(self) -> SimpleCookie:
        jar: SimpleCookie = SimpleCookie()
        for set_cookie in self._response.headers.get_list("set-cookie"):
            jar.load(set_cookie)
        return jar
