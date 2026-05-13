from __future__ import annotations

import sys
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self


TBuilt = TypeVar("TBuilt", covariant=True)


@runtime_checkable
class RequestBuilder(Protocol[TBuilt]):
    def with_method(self, method: str) -> Self: ...  # pragma: no cover
    def with_path(self, path: str) -> Self: ...  # pragma: no cover
    def with_header(self, key: str, value: str) -> Self: ...  # pragma: no cover
    def with_headers(self, headers: dict[str, str]) -> Self: ...  # pragma: no cover
    def with_cookie(self, key: str, value: Any) -> Self: ...  # pragma: no cover
    def with_cookies(self, cookies: dict[str, Any]) -> Self: ...  # pragma: no cover
    def with_query_string(self, params: dict[str, Any]) -> Self: ...  # pragma: no cover
    def with_body(self, body: Any) -> Self: ...  # pragma: no cover
    def build(self) -> TBuilt: ...  # pragma: no cover


class BaseRequestBuilder(Generic[TBuilt]):
    def __init__(
        self,
        method: str = "GET",
        base_url: str | None = None,
        path: str = "/",
        data: dict[str, Any] | None = None,
    ) -> None:
        self._method: str = method.upper()
        self._headers: dict[str, str] = {}
        self._cookies: dict[str, str] = {}
        self._query: dict[str, Any] = {}
        self._body: Any = data
        self._base_url: str | None = base_url
        self._path: str = "/"
        self.with_path(path)

    def with_method(self, method: str) -> Self:
        self._method = method.upper()
        return self

    def with_path(self, path: str) -> Self:
        if self._base_url and not path.startswith(("http://", "https://")):
            path = f"{self._base_url.rstrip('/')}/{path.lstrip('/')}"
        self._path = path
        return self

    def with_header(self, key: str, value: str) -> Self:
        self._headers[key] = value
        return self

    def with_headers(self, headers: dict[str, str]) -> Self:
        self._headers.update(headers)
        return self

    def with_cookie(self, key: str, value: Any) -> Self:
        self._cookies[key] = str(value)
        return self

    def with_cookies(self, cookies: dict[str, Any]) -> Self:
        for k, v in cookies.items():
            self._cookies[k] = str(v)
        return self

    def with_query_string(self, params: dict[str, Any]) -> Self:
        self._query.update(params)
        return self

    def with_body(self, body: Any) -> Self:
        self._body = body
        return self

    def build(self) -> TBuilt:
        raise NotImplementedError("Subclasses must implement build()")  # pragma: no cover
