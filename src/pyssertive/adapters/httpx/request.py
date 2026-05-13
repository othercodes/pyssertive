from __future__ import annotations

from typing import Any

import httpx

from pyssertive.http.request import BaseRequestBuilder


class HttpxRequestBuilder(BaseRequestBuilder[httpx.Request]):
    def build(self) -> httpx.Request:
        kwargs: dict[str, Any] = {
            "method": self._method,
            "url": self._path,
            "headers": self._headers or None,
            "params": self._query or None,
            "cookies": self._cookies or None,
        }
        if self._body is not None:
            kwargs["json"] = self._body
        return httpx.Request(**kwargs)
