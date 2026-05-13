from __future__ import annotations

import sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from django.http import HttpRequest
from django.test import RequestFactory

from pyssertive.http.request import BaseRequestBuilder

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser


class DjangoRequestBuilder(BaseRequestBuilder[HttpRequest]):
    def __init__(
        self,
        rf: RequestFactory | None = None,
        method: str = "GET",
        base_url: str | None = None,
        path: str = "/",
        data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(method=method, base_url=base_url, path=path, data=data)
        self.rf = rf or RequestFactory()
        self._user: AbstractBaseUser | None = None
        self._meta: dict[str, Any] = {}
        self._custom_properties: dict[str, Any] = {}

    def with_user(self, user: AbstractBaseUser) -> Self:
        self._user = user
        return self

    def with_meta(self, key: str, value: Any) -> Self:
        self._meta[key] = str(value)
        return self

    def with_property(self, name: str, value: Any) -> Self:
        self._custom_properties[name] = value
        return self

    def build(self) -> HttpRequest:
        import json
        from urllib.parse import urlencode

        method_map: dict[str, Callable[..., HttpRequest]] = {
            "GET": self.rf.get,
            "POST": self.rf.post,
            "PUT": self.rf.put,
            "PATCH": self.rf.patch,
            "DELETE": self.rf.delete,
            "HEAD": self.rf.head,
            "OPTIONS": self.rf.options,
        }
        if self._method not in method_map:
            raise ValueError(f"Unsupported HTTP method: {self._method}")

        path = self._path
        if self._query:
            qs = urlencode(self._query, doseq=True)
            path = f"{path}{'&' if '?' in path else '?'}{qs}"

        content_type = self._headers.get("Content-Type") or self._headers.get("content-type")
        body: Any = self._body if self._body is not None else {}
        rf_call = method_map[self._method]
        if content_type and "application/json" in content_type and isinstance(body, dict):
            body = json.dumps(body).encode("utf-8")
            request: HttpRequest = rf_call(path, body, content_type=content_type, headers=self._headers)
        else:
            request = rf_call(path, body, headers=self._headers)

        if self._user:
            request.user = self._user  # type: ignore[assignment]
        for key, value in self._cookies.items():
            request.COOKIES[key] = value
        for key, value in self._meta.items():
            request.META[key] = value
        for key, value in self._custom_properties.items():
            setattr(request, key, value)

        return request
