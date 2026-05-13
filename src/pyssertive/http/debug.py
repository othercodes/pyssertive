from __future__ import annotations

import json
import pprint
import sys
from json import JSONDecodeError
from typing import Any

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self


class DebugResponseMixin:
    status_code: int
    headers: Any
    content: bytes
    cookies: Any

    def dump(self, content_format: str | None = None) -> Self:
        content_type = content_format or self.headers.get("Content-Type", "")

        print("\n[Response Dump - format:", content_type, "]")
        print("[Status]", self.status_code)
        print("[Headers]", dict(self.headers))

        match content_type:
            case "application/json":
                try:
                    pprint.pprint(json.loads(self.content))
                except JSONDecodeError:
                    print("[Invalid JSON]", self.content.decode(errors="replace"))
            case "text/plain":
                print(self.content.decode(errors="replace"))
            case _:
                print(repr(self.content))

        return self

    def dump_headers(self) -> Self:
        print("\n[Response Headers]")
        for key, value in self.headers.items():
            print(f"  {key}: {value}")
        return self

    def dump_json(self) -> Self:
        print("\n[Response JSON]")
        try:
            data = json.loads(self.content)
            print(json.dumps(data, indent=2, default=str))
        except JSONDecodeError:
            raise AssertionError("Response content is not valid JSON") from None
        return self

    def dump_cookies(self) -> Self:
        print("\n[Response Cookies]")
        cookies = self.cookies
        if cookies:
            for name, cookie in cookies.items():
                print(f"  {name}: {cookie.value}")
                if cookie.get("max-age"):
                    print(f"    max-age: {cookie['max-age']}")
                if cookie.get("path"):  # pragma: no branch
                    print(f"    path: {cookie['path']}")
        else:
            print("  (none)")
        return self

    def dd(self) -> None:
        self.dump()
        raise RuntimeError("dd() called - stopping execution")
