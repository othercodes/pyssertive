from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Any

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

from pyssertive.protocols.mcp.content import AssertableContent


class AssertableToolDef:
    def __init__(self, definition: dict[str, Any]) -> None:
        self._definition = definition

    @property
    def _name(self) -> str:
        name = self._definition.get("name", "<unknown>")
        return name if isinstance(name, str) else "<unknown>"

    def documented(self) -> Self:
        description = self._definition.get("description")
        if not description:
            raise AssertionError(f"Tool '{self._name}' has no description")
        return self

    def accepts(self, params: list[str]) -> Self:
        required = list((self._definition.get("inputSchema") or {}).get("required") or [])
        missing = [p for p in params if p not in required]
        if missing:
            raise AssertionError(f"Tool '{self._name}' does not require parameters {missing!r}; required={required!r}")
        return self

    def accepts_optional(self, params: list[str]) -> Self:
        properties = list((self._definition.get("inputSchema") or {}).get("properties") or {})
        missing = [p for p in params if p not in properties]
        if missing:
            raise AssertionError(f"Tool '{self._name}' has no input properties {missing!r}; properties={properties!r}")
        return self

    def does_not_accept(self, params: list[str]) -> Self:
        properties = list((self._definition.get("inputSchema") or {}).get("properties") or {})
        present = [p for p in params if p in properties]
        if present:
            raise AssertionError(
                f"Tool '{self._name}' should not expose properties {present!r}; properties={properties!r}"
            )
        return self

    def has_output_schema(self) -> Self:
        if not self._definition.get("outputSchema"):
            raise AssertionError(f"Tool '{self._name}' has no outputSchema")
        return self


class AssertableToolList:
    def __init__(self, result: dict[str, Any]) -> None:
        self._result = result
        tools = result.get("tools")
        if not isinstance(tools, list):
            raise AssertionError("Response result is missing 'tools' list — not a tools/list response")
        self._tools: list[dict[str, Any]] = tools

    def with_count(self, expected: int) -> Self:
        actual = len(self._tools)
        if actual != expected:
            raise AssertionError(f"Expected {expected} tools, got {actual}")
        return self

    def contains_tool(
        self,
        name: str,
        callback: Callable[[AssertableToolDef], Any] | None = None,
    ) -> Self:
        match = next((t for t in self._tools if isinstance(t, dict) and t.get("name") == name), None)
        if match is None:
            names = [t.get("name") for t in self._tools if isinstance(t, dict)]
            raise AssertionError(f"Tool '{name}' not found in tools list. Available: {names!r}")
        if callback is not None:
            callback(AssertableToolDef(match))
        return self

    def does_not_contain_tool(self, name: str) -> Self:
        if any(isinstance(t, dict) and t.get("name") == name for t in self._tools):
            raise AssertionError(f"Tool '{name}' should not be in tools list, but it was found")
        return self

    def every_tool(self, callback: Callable[[AssertableToolDef], Any]) -> Self:
        for tool in self._tools:
            if isinstance(tool, dict):
                callback(AssertableToolDef(tool))
        return self

    def has_more_pages(self) -> Self:
        if not self._result.get("nextCursor"):
            raise AssertionError("Expected tools/list response to advertise a nextCursor")
        return self


class AssertableToolCall:
    def __init__(
        self,
        *,
        name: str,
        result: dict[str, Any] | None,
        error: dict[str, Any] | None,
    ) -> None:
        self._name = name
        self._result = result
        self._error = error

    def _require_result(self) -> dict[str, Any]:
        if self._error is not None:
            raise AssertionError(
                f"Tool '{self._name}' returned a protocol error "
                f"({self._error.get('code')}): {self._error.get('message')!r}"
            )
        if self._result is None:
            raise AssertionError(f"Tool '{self._name}' response has no result payload")
        return self._result

    def _require_error(self) -> dict[str, Any]:
        if self._error is None:
            raise AssertionError(f"Expected protocol-level error for tool '{self._name}', got success result")
        return self._error

    def _content_blocks(self) -> list[Any]:
        result = self._require_result()
        if result.get("isError") is True:
            raise AssertionError(
                f"Tool '{self._name}' reported a tool error (isError=true); use reports_tool_error() to assert it"
            )
        content = result.get("content")
        if not isinstance(content, list):
            raise AssertionError(f"Tool '{self._name}' response has no content list")
        return content

    def succeeds(self) -> Self:
        result = self._require_result()
        if result.get("isError") is True:
            raise AssertionError(f"Tool '{self._name}' reported isError=true; expected success")
        return self

    def returns_text(self, expected: str) -> Self:
        for block in self._content_blocks():
            if isinstance(block, dict) and block.get("type") == "text" and block.get("text") == expected:
                return self
        texts = [b.get("text") for b in self._content_blocks() if isinstance(b, dict) and b.get("type") == "text"]
        raise AssertionError(f"Tool '{self._name}' did not return text {expected!r}. Got text blocks: {texts!r}")

    def returns_text_containing(self, substr: str) -> Self:
        for block in self._content_blocks():
            if isinstance(block, dict) and block.get("type") == "text" and substr in (block.get("text") or ""):
                return self
        texts = [b.get("text") for b in self._content_blocks() if isinstance(b, dict) and b.get("type") == "text"]
        raise AssertionError(f"Tool '{self._name}' did not return any text block containing {substr!r}. Got: {texts!r}")

    def returns_image(self, *, mime_type: str | None = None) -> Self:
        for block in self._content_blocks():
            if (
                isinstance(block, dict)
                and block.get("type") == "image"
                and (mime_type is None or block.get("mimeType") == mime_type)
            ):
                return self
        raise AssertionError(
            f"Tool '{self._name}' did not return an image block"
            + (f" with mimeType {mime_type!r}" if mime_type else "")
        )

    def returns_content_count(self, expected: int) -> Self:
        actual = len(self._content_blocks())
        if actual != expected:
            raise AssertionError(f"Tool '{self._name}' returned {actual} content blocks, expected {expected}")
        return self

    def returns_structured(self, expected: Any) -> Self:
        result = self._require_result()
        actual = result.get("structuredContent")
        if actual != expected:
            raise AssertionError(f"Tool '{self._name}' structuredContent: expected {expected!r}, got {actual!r}")
        return self

    def content(self, index: int, callback: Callable[[AssertableContent], Any]) -> Self:
        blocks = self._content_blocks()
        if index >= len(blocks) or index < -len(blocks):
            raise AssertionError(f"Tool '{self._name}' content index {index} out of range (len={len(blocks)})")
        callback(AssertableContent(blocks[index], index=index))
        return self

    def reports_tool_error(self) -> Self:
        result = self._require_result()
        if result.get("isError") is not True:
            raise AssertionError(f"Tool '{self._name}' did not report isError=true; got result={result!r}")
        return self

    def with_message_containing(self, substr: str) -> Self:
        if self._error is not None:
            message = self._error.get("message") or ""
            if substr not in message:
                raise AssertionError(f"Tool '{self._name}' error message does not contain {substr!r}: {message!r}")
            return self
        result = self._require_result()
        content = result.get("content") or []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text" and substr in (block.get("text") or ""):
                return self
        raise AssertionError(f"Tool '{self._name}' tool-error message does not contain {substr!r}; content={content!r}")

    def is_rejected_as_unknown_tool(self) -> Self:
        error = self._require_error()
        code = error.get("code")
        message = (error.get("message") or "").lower()
        if code == -32601:
            return self
        if code == -32602 and ("unknown tool" in message or "not found" in message):
            return self
        raise AssertionError(
            f"Expected unknown-tool rejection for '{self._name}', got code={code} message={error.get('message')!r}"
        )

    def is_rejected_with_invalid_params(self) -> Self:
        error = self._require_error()
        if error.get("code") != -32602:
            raise AssertionError(f"Expected invalid-params (-32602) for '{self._name}', got code={error.get('code')}")
        return self
