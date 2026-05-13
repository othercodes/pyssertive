from __future__ import annotations

import base64
import binascii
import sys
from typing import Any

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self


class AssertableContent:
    def __init__(self, block: Any, *, index: int) -> None:
        self._block = block
        self._index = index

    def _require_type(self, expected: str) -> dict[str, Any]:
        if not isinstance(self._block, dict):
            raise AssertionError(f"Content block at index {self._index} is not a dict: {self._block!r}")
        actual = self._block.get("type") or "<unknown>"
        if actual != expected:
            raise AssertionError(f"Content block at index {self._index} is of type '{actual}', expected '{expected}'")
        return self._block

    def is_text(self) -> Self:
        self._require_type("text")
        return self

    def is_image(self) -> Self:
        self._require_type("image")
        return self

    def is_audio(self) -> Self:
        self._require_type("audio")
        return self

    def is_resource_link(self) -> Self:
        self._require_type("resource_link")
        return self

    def is_resource(self) -> Self:
        self._require_type("resource")
        return self

    def text_equals(self, expected: str) -> Self:
        block = self._require_type("text")
        actual = block.get("text", "")
        if actual != expected:
            raise AssertionError(f"Content[{self._index}].text: expected {expected!r}, got {actual!r}")
        return self

    def text_contains(self, substr: str) -> Self:
        block = self._require_type("text")
        actual = block.get("text", "")
        if substr not in actual:
            raise AssertionError(f"Content[{self._index}].text does not contain {substr!r}: {actual!r}")
        return self

    def with_mime_type(self, expected: str) -> Self:
        if not isinstance(self._block, dict):
            raise AssertionError(f"Content block at index {self._index} is not a dict")
        actual = self._block.get("mimeType")
        if actual != expected:
            raise AssertionError(f"Content[{self._index}].mimeType: expected {expected!r}, got {actual!r}")
        return self

    def with_base64_data(self) -> Self:
        if not isinstance(self._block, dict):
            raise AssertionError(f"Content block at index {self._index} is not a dict")
        data = self._block.get("data")
        if not isinstance(data, str) or not data:
            raise AssertionError(f"Content[{self._index}].data missing or empty")
        try:
            base64.b64decode(data, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise AssertionError(f"Content[{self._index}].data is not valid base64: {exc}") from exc
        return self

    def with_uri(self, expected: str) -> Self:
        if not isinstance(self._block, dict):
            raise AssertionError(f"Content block at index {self._index} is not a dict")
        block_type = self._block.get("type")
        actual = (self._block.get("resource") or {}).get("uri") if block_type == "resource" else self._block.get("uri")
        if actual != expected:
            raise AssertionError(f"Content[{self._index}].uri: expected {expected!r}, got {actual!r}")
        return self
