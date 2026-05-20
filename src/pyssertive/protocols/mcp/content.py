from __future__ import annotations

import base64
import binascii
import sys
from typing import Any

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


class AssertableContent:
    """Fluent assertions over a single MCP content block.

    Value-asserting methods auto-dispatch based on the block's `type` field.
    Compatibility:

    | Method                                                            | Compatible types                          |
    |-------------------------------------------------------------------|-------------------------------------------|
    | is_text / is_image / is_audio / is_resource_link / is_resource    | standalone type guards                    |
    | with_text / with_text_containing                                  | text, resource                            |
    | is_not_empty                                                      | text, resource, image, audio              |
    | with_mime_type                                                    | image, audio, resource_link, resource     |
    | with_uri / named                                                  | resource_link, resource                   |
    | with_base64_data                                                  | image, audio                              |
    | with_blob_data                                                    | resource                                  |

    Calling a method on an incompatible block raises AssertionError listing the
    expected types and the actual type observed.
    """

    def __init__(self, block: Any, *, label: str) -> None:
        self._block = block
        self._label = label

    def _block_type(self) -> str:
        if not isinstance(self._block, dict):
            raise AssertionError(f"{self._label} is not a dict: {self._block!r}")
        actual = self._block.get("type") or "<unknown>"
        return actual if isinstance(actual, str) else "<unknown>"

    def _require_type(self, expected: str) -> None:
        actual = self._block_type()
        if actual != expected:
            raise AssertionError(f"{self._label} is of type {actual!r}, expected {expected!r}")

    def _require_one_of(self, expected: list[str], method: str) -> str:
        actual = self._block_type()
        if actual not in expected:
            raise AssertionError(f"{self._label}.{method}() requires type in {expected!r}, got {actual!r}")
        return actual

    def _resource_inner(self) -> dict[str, Any]:
        inner = self._block.get("resource") if isinstance(self._block, dict) else None
        if not isinstance(inner, dict):
            raise AssertionError(f"{self._label}.resource is not a dict: {inner!r}")
        return inner

    def _text_payload(self, method: str) -> str:
        type_ = self._require_one_of(["text", "resource"], method)
        text = self._block.get("text", "") if type_ == "text" else self._resource_inner().get("text", "")
        return text if isinstance(text, str) else ""

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

    def with_text(self, expected: str) -> Self:
        actual = self._text_payload("with_text")
        if actual != expected:
            raise AssertionError(f"{self._label}.text: expected {expected!r}, got {actual!r}")
        return self

    def with_text_containing(self, substr: str) -> Self:
        actual = self._text_payload("with_text_containing")
        if substr not in actual:
            raise AssertionError(f"{self._label}.text does not contain {substr!r}: {actual!r}")
        return self

    def is_not_empty(self) -> Self:
        type_ = self._require_one_of(["text", "resource", "image", "audio"], "is_not_empty")
        if type_ == "text":
            candidates = [self._block.get("text")]
        elif type_ == "resource":
            inner = self._resource_inner()
            candidates = [inner.get("text"), inner.get("blob")]
        else:
            candidates = [self._block.get("data")]
        if not any(isinstance(c, str) and c for c in candidates):
            raise AssertionError(f"{self._label} ({type_}) has empty payload")
        return self

    def with_mime_type(self, expected: str) -> Self:
        type_ = self._require_one_of(["image", "audio", "resource_link", "resource"], "with_mime_type")
        actual = self._resource_inner().get("mimeType") if type_ == "resource" else self._block.get("mimeType")
        if actual != expected:
            raise AssertionError(f"{self._label}.mimeType: expected {expected!r}, got {actual!r}")
        return self

    def with_base64_data(self) -> Self:
        self._require_one_of(["image", "audio"], "with_base64_data")
        _check_base64(self._block.get("data"), label=self._label, field="data")
        return self

    def with_blob_data(self) -> Self:
        self._require_one_of(["resource"], "with_blob_data")
        _check_base64(self._resource_inner().get("blob"), label=self._label, field="blob")
        return self

    def with_uri(self, expected: str) -> Self:
        type_ = self._require_one_of(["resource_link", "resource"], "with_uri")
        actual = self._block.get("uri") if type_ == "resource_link" else self._resource_inner().get("uri")
        if actual != expected:
            raise AssertionError(f"{self._label}.uri: expected {expected!r}, got {actual!r}")
        return self

    def named(self, expected: str) -> Self:
        type_ = self._require_one_of(["resource_link", "resource"], "named")
        actual = self._block.get("name") if type_ == "resource_link" else self._resource_inner().get("name")
        if actual != expected:
            raise AssertionError(f"{self._label}.name: expected {expected!r}, got {actual!r}")
        return self
