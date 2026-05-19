from __future__ import annotations

import base64
import binascii
import sys
from collections.abc import Callable
from typing import Any, overload

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self


def _check_base64(data: Any, *, index: int, field: str) -> None:
    if not isinstance(data, str) or not data:
        raise AssertionError(f"Content[{index}].{field} missing or empty")
    try:
        base64.b64decode(data, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise AssertionError(f"Content[{index}].{field} is not valid base64: {exc}") from exc


class AssertableTextContent:
    def __init__(self, block: dict[str, Any], *, index: int) -> None:
        self._block = block
        self._index = index

    def text_equals(self, expected: str) -> Self:
        actual = self._block.get("text", "")
        if actual != expected:
            raise AssertionError(f"Content[{self._index}].text: expected {expected!r}, got {actual!r}")
        return self

    def text_contains(self, substr: str) -> Self:
        actual = self._block.get("text", "")
        if substr not in actual:
            raise AssertionError(f"Content[{self._index}].text does not contain {substr!r}: {actual!r}")
        return self

    def is_not_empty(self) -> Self:
        actual = self._block.get("text") or ""
        if not actual:
            raise AssertionError(f"Content[{self._index}].text is empty")
        return self


class AssertableImageContent:
    def __init__(self, block: dict[str, Any], *, index: int) -> None:
        self._block = block
        self._index = index

    def with_mime_type(self, expected: str) -> Self:
        actual = self._block.get("mimeType")
        if actual != expected:
            raise AssertionError(f"Content[{self._index}].mimeType: expected {expected!r}, got {actual!r}")
        return self

    def with_base64_data(self) -> Self:
        _check_base64(self._block.get("data"), index=self._index, field="data")
        return self


class AssertableAudioContent:
    def __init__(self, block: dict[str, Any], *, index: int) -> None:
        self._block = block
        self._index = index

    def with_mime_type(self, expected: str) -> Self:
        actual = self._block.get("mimeType")
        if actual != expected:
            raise AssertionError(f"Content[{self._index}].mimeType: expected {expected!r}, got {actual!r}")
        return self

    def with_base64_data(self) -> Self:
        _check_base64(self._block.get("data"), index=self._index, field="data")
        return self


class AssertableResourceLinkContent:
    def __init__(self, block: dict[str, Any], *, index: int) -> None:
        self._block = block
        self._index = index

    def with_uri(self, expected: str) -> Self:
        actual = self._block.get("uri")
        if actual != expected:
            raise AssertionError(f"Content[{self._index}].uri: expected {expected!r}, got {actual!r}")
        return self

    def named(self, expected: str) -> Self:
        actual = self._block.get("name")
        if actual != expected:
            raise AssertionError(f"Content[{self._index}].name: expected {expected!r}, got {actual!r}")
        return self

    def with_mime_type(self, expected: str) -> Self:
        actual = self._block.get("mimeType")
        if actual != expected:
            raise AssertionError(f"Content[{self._index}].mimeType: expected {expected!r}, got {actual!r}")
        return self


class AssertableResourceContent:
    def __init__(self, block: dict[str, Any], *, index: int) -> None:
        self._block = block
        self._index = index

    @property
    def _resource(self) -> dict[str, Any]:
        inner = self._block.get("resource") or {}
        return inner if isinstance(inner, dict) else {}

    def with_uri(self, expected: str) -> Self:
        actual = self._resource.get("uri")
        if actual != expected:
            raise AssertionError(f"Content[{self._index}].uri: expected {expected!r}, got {actual!r}")
        return self

    def with_mime_type(self, expected: str) -> Self:
        actual = self._resource.get("mimeType")
        if actual != expected:
            raise AssertionError(f"Content[{self._index}].mimeType: expected {expected!r}, got {actual!r}")
        return self

    def with_text(self, expected: str) -> Self:
        actual = self._resource.get("text")
        if actual != expected:
            raise AssertionError(f"Content[{self._index}].text: expected {expected!r}, got {actual!r}")
        return self

    def with_text_containing(self, substr: str) -> Self:
        actual = self._resource.get("text") or ""
        if substr not in actual:
            raise AssertionError(f"Content[{self._index}].text does not contain {substr!r}: {actual!r}")
        return self

    def with_blob_data(self) -> Self:
        _check_base64(self._resource.get("blob"), index=self._index, field="blob")
        return self


class AssertableContent:
    def __init__(self, block: Any, *, index: int) -> None:
        self._block = block
        self._index = index

    def _require_type(self, expected: str) -> None:
        if not isinstance(self._block, dict):
            raise AssertionError(f"Content block at index {self._index} is not a dict: {self._block!r}")
        actual = self._block.get("type") or "<unknown>"
        if actual != expected:
            raise AssertionError(f"Content block at index {self._index} is of type {actual!r}, expected {expected!r}")

    @overload
    def is_text(self) -> AssertableTextContent: ...
    @overload
    def is_text(self, callback: Callable[[AssertableTextContent], Any]) -> Self: ...
    def is_text(self, callback: Callable[[AssertableTextContent], Any] | None = None) -> AssertableTextContent | Self:
        self._require_type("text")
        typed = AssertableTextContent(self._block, index=self._index)
        if callback is None:
            return typed
        callback(typed)
        return self

    @overload
    def is_image(self) -> AssertableImageContent: ...
    @overload
    def is_image(self, callback: Callable[[AssertableImageContent], Any]) -> Self: ...
    def is_image(
        self, callback: Callable[[AssertableImageContent], Any] | None = None
    ) -> AssertableImageContent | Self:
        self._require_type("image")
        typed = AssertableImageContent(self._block, index=self._index)
        if callback is None:
            return typed
        callback(typed)
        return self

    @overload
    def is_audio(self) -> AssertableAudioContent: ...
    @overload
    def is_audio(self, callback: Callable[[AssertableAudioContent], Any]) -> Self: ...
    def is_audio(
        self, callback: Callable[[AssertableAudioContent], Any] | None = None
    ) -> AssertableAudioContent | Self:
        self._require_type("audio")
        typed = AssertableAudioContent(self._block, index=self._index)
        if callback is None:
            return typed
        callback(typed)
        return self

    @overload
    def is_resource_link(self) -> AssertableResourceLinkContent: ...
    @overload
    def is_resource_link(self, callback: Callable[[AssertableResourceLinkContent], Any]) -> Self: ...
    def is_resource_link(
        self, callback: Callable[[AssertableResourceLinkContent], Any] | None = None
    ) -> AssertableResourceLinkContent | Self:
        self._require_type("resource_link")
        typed = AssertableResourceLinkContent(self._block, index=self._index)
        if callback is None:
            return typed
        callback(typed)
        return self

    @overload
    def is_resource(self) -> AssertableResourceContent: ...
    @overload
    def is_resource(self, callback: Callable[[AssertableResourceContent], Any]) -> Self: ...
    def is_resource(
        self, callback: Callable[[AssertableResourceContent], Any] | None = None
    ) -> AssertableResourceContent | Self:
        self._require_type("resource")
        typed = AssertableResourceContent(self._block, index=self._index)
        if callback is None:
            return typed
        callback(typed)
        return self
