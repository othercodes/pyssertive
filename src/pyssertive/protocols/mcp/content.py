from __future__ import annotations

import base64
import binascii
import sys
from collections.abc import Callable
from typing import Any, ClassVar, overload

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self


def _check_base64(data: Any, *, label: str, field: str) -> None:
    if not isinstance(data, str) or not data:
        raise AssertionError(f"{label}.{field} missing or empty")
    try:
        base64.b64decode(data, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise AssertionError(f"{label}.{field} is not valid base64: {exc}") from exc


def _validate_block(block: Any, *, label: str, expected_type: str) -> dict[str, Any]:
    if not isinstance(block, dict):
        raise AssertionError(f"{label} is not a dict: {block!r}")
    actual = block.get("type") or "<unknown>"
    if actual != expected_type:
        raise AssertionError(f"{label} is of type {actual!r}, expected {expected_type!r}")
    return block


class AssertableTextContent:
    def __init__(self, block: Any, *, label: str) -> None:
        self._block = _validate_block(block, label=label, expected_type="text")
        self._label = label

    def with_text(self, expected: str) -> Self:
        actual = self._block.get("text", "")
        if actual != expected:
            raise AssertionError(f"{self._label}.text: expected {expected!r}, got {actual!r}")
        return self

    def with_text_containing(self, substr: str) -> Self:
        actual = self._block.get("text", "")
        if substr not in actual:
            raise AssertionError(f"{self._label}.text does not contain {substr!r}: {actual!r}")
        return self

    def is_not_empty(self) -> Self:
        actual = self._block.get("text") or ""
        if not actual:
            raise AssertionError(f"{self._label}.text is empty")
        return self


class _MediaContent:
    """Shared base for image/audio content blocks: {type, mimeType, data:base64}."""

    _BLOCK_TYPE: ClassVar[str]

    def __init__(self, block: Any, *, label: str) -> None:
        self._block = _validate_block(block, label=label, expected_type=self._BLOCK_TYPE)
        self._label = label

    def with_mime_type(self, expected: str) -> Self:
        actual = self._block.get("mimeType")
        if actual != expected:
            raise AssertionError(f"{self._label}.mimeType: expected {expected!r}, got {actual!r}")
        return self

    def with_base64_data(self) -> Self:
        _check_base64(self._block.get("data"), label=self._label, field="data")
        return self


class AssertableImageContent(_MediaContent):
    _BLOCK_TYPE: ClassVar[str] = "image"


class AssertableAudioContent(_MediaContent):
    _BLOCK_TYPE: ClassVar[str] = "audio"


class AssertableResourceLinkContent:
    def __init__(self, block: Any, *, label: str) -> None:
        self._block = _validate_block(block, label=label, expected_type="resource_link")
        self._label = label

    def with_uri(self, expected: str) -> Self:
        actual = self._block.get("uri")
        if actual != expected:
            raise AssertionError(f"{self._label}.uri: expected {expected!r}, got {actual!r}")
        return self

    def named(self, expected: str) -> Self:
        actual = self._block.get("name")
        if actual != expected:
            raise AssertionError(f"{self._label}.name: expected {expected!r}, got {actual!r}")
        return self

    def with_mime_type(self, expected: str) -> Self:
        actual = self._block.get("mimeType")
        if actual != expected:
            raise AssertionError(f"{self._label}.mimeType: expected {expected!r}, got {actual!r}")
        return self


class AssertableResourceContent:
    def __init__(self, block: Any, *, label: str) -> None:
        self._block = _validate_block(block, label=label, expected_type="resource")
        self._label = label
        inner = self._block.get("resource")
        if not isinstance(inner, dict):
            raise AssertionError(f"{label}.resource is not a dict: {inner!r}")
        self._resource: dict[str, Any] = inner

    def with_uri(self, expected: str) -> Self:
        actual = self._resource.get("uri")
        if actual != expected:
            raise AssertionError(f"{self._label}.uri: expected {expected!r}, got {actual!r}")
        return self

    def with_mime_type(self, expected: str) -> Self:
        actual = self._resource.get("mimeType")
        if actual != expected:
            raise AssertionError(f"{self._label}.mimeType: expected {expected!r}, got {actual!r}")
        return self

    def with_text(self, expected: str) -> Self:
        actual = self._resource.get("text")
        if actual != expected:
            raise AssertionError(f"{self._label}.text: expected {expected!r}, got {actual!r}")
        return self

    def with_text_containing(self, substr: str) -> Self:
        actual = self._resource.get("text") or ""
        if substr not in actual:
            raise AssertionError(f"{self._label}.text does not contain {substr!r}: {actual!r}")
        return self

    def with_blob_data(self) -> Self:
        _check_base64(self._resource.get("blob"), label=self._label, field="blob")
        return self


class AssertableContent:
    def __init__(self, block: Any, *, label: str) -> None:
        self._block = block
        self._label = label

    @overload
    def is_text(self) -> AssertableTextContent: ...
    @overload
    def is_text(self, callback: Callable[[AssertableTextContent], Any]) -> Self: ...
    def is_text(self, callback: Callable[[AssertableTextContent], Any] | None = None) -> AssertableTextContent | Self:
        typed = AssertableTextContent(self._block, label=self._label)
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
        typed = AssertableImageContent(self._block, label=self._label)
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
        typed = AssertableAudioContent(self._block, label=self._label)
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
        typed = AssertableResourceLinkContent(self._block, label=self._label)
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
        typed = AssertableResourceContent(self._block, label=self._label)
        if callback is None:
            return typed
        callback(typed)
        return self
