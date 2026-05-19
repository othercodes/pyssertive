from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Any

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

from pyssertive.protocols.mcp.content import (
    AssertableAudioContent,
    AssertableContent,
    AssertableImageContent,
    AssertableResourceContent,
    AssertableResourceLinkContent,
    AssertableTextContent,
)


class AssertablePromptDef:
    def __init__(self, definition: dict[str, Any]) -> None:
        self._definition = definition

    @property
    def _name(self) -> str:
        name = self._definition.get("name", "<unknown>")
        return name if isinstance(name, str) else "<unknown>"

    def _arguments(self) -> list[dict[str, Any]]:
        args = self._definition.get("arguments") or []
        return [a for a in args if isinstance(a, dict)]

    def documented(self) -> Self:
        description = self._definition.get("description")
        if not description:
            raise AssertionError(f"Prompt '{self._name}' has no description")
        return self

    def accepts(self, params: list[str]) -> Self:
        required = [a.get("name") for a in self._arguments() if a.get("required") is True]
        missing = [p for p in params if p not in required]
        if missing:
            raise AssertionError(f"Prompt '{self._name}' does not require arguments {missing!r}; required={required!r}")
        return self

    def accepts_optional(self, params: list[str]) -> Self:
        optional = [a.get("name") for a in self._arguments() if a.get("required") is not True]
        missing = [p for p in params if p not in optional]
        if missing:
            raise AssertionError(f"Prompt '{self._name}' has no optional arguments {missing!r}; optional={optional!r}")
        return self

    def does_not_accept(self, params: list[str]) -> Self:
        names = [a.get("name") for a in self._arguments()]
        present = [p for p in params if p in names]
        if present:
            raise AssertionError(f"Prompt '{self._name}' should not expose arguments {present!r}; arguments={names!r}")
        return self


class AssertablePromptList:
    def __init__(self, result: dict[str, Any]) -> None:
        self._result = result
        prompts = result.get("prompts")
        if not isinstance(prompts, list):
            raise AssertionError("Response result is missing 'prompts' list — not a prompts/list response")
        self._prompts: list[dict[str, Any]] = prompts

    def with_count(self, expected: int) -> Self:
        actual = len(self._prompts)
        if actual != expected:
            raise AssertionError(f"Expected {expected} prompts, got {actual}")
        return self

    def contains_prompt(
        self,
        name: str,
        callback: Callable[[AssertablePromptDef], Any] | None = None,
    ) -> Self:
        match = next((p for p in self._prompts if isinstance(p, dict) and p.get("name") == name), None)
        if match is None:
            names = [p.get("name") for p in self._prompts if isinstance(p, dict)]
            raise AssertionError(f"Prompt '{name}' not found in prompts list. Available: {names!r}")
        if callback is not None:
            callback(AssertablePromptDef(match))
        return self

    def does_not_contain_prompt(self, name: str) -> Self:
        if any(isinstance(p, dict) and p.get("name") == name for p in self._prompts):
            raise AssertionError(f"Prompt '{name}' should not be in prompts list, but it was found")
        return self

    def every_prompt(self, callback: Callable[[AssertablePromptDef], Any]) -> Self:
        for prompt in self._prompts:
            if isinstance(prompt, dict):
                callback(AssertablePromptDef(prompt))
        return self

    def has_more_pages(self) -> Self:
        if not self._result.get("nextCursor"):
            raise AssertionError("Expected prompts/list response to advertise a nextCursor")
        return self


class AssertablePromptMessage:
    def __init__(self, message: Any, *, index: int) -> None:
        self._message = message
        self._index = index

    def _require_dict(self) -> dict[str, Any]:
        if not isinstance(self._message, dict):
            raise AssertionError(f"Message[{self._index}] is not a dict: {self._message!r}")
        return self._message

    def _content_block(self) -> dict[str, Any]:
        msg = self._require_dict()
        content = msg.get("content")
        if not isinstance(content, dict):
            raise AssertionError(f"Message[{self._index}].content is not a dict: {content!r}")
        return content

    def _assertable_content(self) -> AssertableContent:
        return AssertableContent(self._content_block(), label=f"Message[{self._index}].content")

    def is_from_user(self) -> Self:
        role = self._require_dict().get("role")
        if role != "user":
            raise AssertionError(f"Message[{self._index}] role: expected 'user', got {role!r}")
        return self

    def is_from_assistant(self) -> Self:
        role = self._require_dict().get("role")
        if role != "assistant":
            raise AssertionError(f"Message[{self._index}] role: expected 'assistant', got {role!r}")
        return self

    def has_text(self) -> Self:
        self._assertable_content().is_text().is_not_empty()
        return self

    def with_text(self, expected: str) -> Self:
        self._assertable_content().is_text().with_text(expected)
        return self

    def with_text_containing(self, substr: str) -> Self:
        self._assertable_content().is_text().with_text_containing(substr)
        return self

    def content(self, callback: Callable[[AssertableContent], Any] | None = None) -> AssertableContent | Self:
        typed = self._assertable_content()
        if callback is None:
            return typed
        callback(typed)
        return self

    def is_text(self, callback: Callable[[AssertableTextContent], Any] | None = None) -> AssertableTextContent | Self:
        content = self._assertable_content()
        if callback is None:
            return content.is_text()
        content.is_text(callback)
        return self

    def is_image(
        self, callback: Callable[[AssertableImageContent], Any] | None = None
    ) -> AssertableImageContent | Self:
        content = self._assertable_content()
        if callback is None:
            return content.is_image()
        content.is_image(callback)
        return self

    def is_audio(
        self, callback: Callable[[AssertableAudioContent], Any] | None = None
    ) -> AssertableAudioContent | Self:
        content = self._assertable_content()
        if callback is None:
            return content.is_audio()
        content.is_audio(callback)
        return self

    def is_resource_link(
        self, callback: Callable[[AssertableResourceLinkContent], Any] | None = None
    ) -> AssertableResourceLinkContent | Self:
        content = self._assertable_content()
        if callback is None:
            return content.is_resource_link()
        content.is_resource_link(callback)
        return self

    def is_resource(
        self, callback: Callable[[AssertableResourceContent], Any] | None = None
    ) -> AssertableResourceContent | Self:
        content = self._assertable_content()
        if callback is None:
            return content.is_resource()
        content.is_resource(callback)
        return self


class AssertablePromptGet:
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
                f"Prompt '{self._name}' returned a protocol error "
                f"({self._error.get('code')}): {self._error.get('message')!r}"
            )
        if self._result is None:
            # MCP methods never return `result: null` — every method has a typed result shape
            # (even `ping` returns `{}`). Treating null as malformed catches server bugs early.
            raise AssertionError(f"Prompt '{self._name}' response has no result payload")
        return self._result

    def _require_error(self) -> dict[str, Any]:
        if self._error is None:
            raise AssertionError(f"Expected protocol-level error for prompt '{self._name}', got success result")
        return self._error

    def _messages(self) -> list[Any]:
        result = self._require_result()
        messages = result.get("messages")
        if not isinstance(messages, list):
            raise AssertionError(f"Prompt '{self._name}' response has no messages list")
        return messages

    def _message_at(self, index: int) -> AssertablePromptMessage:
        messages = self._messages()
        if index >= len(messages) or index < -len(messages):
            raise AssertionError(f"Prompt '{self._name}' message index {index} out of range (len={len(messages)})")
        actual_index = index if index >= 0 else len(messages) + index
        return AssertablePromptMessage(messages[index], index=actual_index)

    def _drill_message(
        self,
        index: int,
        callback: Callable[[AssertablePromptMessage], Any] | None,
    ) -> AssertablePromptMessage | Self:
        msg = self._message_at(index)
        if callback is None:
            return msg
        callback(msg)
        return self

    def with_description(self, expected: str) -> Self:
        actual = self._require_result().get("description")
        if actual != expected:
            raise AssertionError(f"Prompt '{self._name}' description: expected {expected!r}, got {actual!r}")
        return self

    def with_description_containing(self, substr: str) -> Self:
        actual = self._require_result().get("description") or ""
        if substr not in actual:
            raise AssertionError(f"Prompt '{self._name}' description does not contain {substr!r}: {actual!r}")
        return self

    def succeeds(self) -> Self:
        self._require_result()
        return self

    def with_message_count(self, expected: int) -> Self:
        actual = len(self._messages())
        if actual != expected:
            raise AssertionError(f"Prompt '{self._name}' expected {expected} messages, got {actual}")
        return self

    def first_message(
        self, callback: Callable[[AssertablePromptMessage], Any] | None = None
    ) -> AssertablePromptMessage | Self:
        return self._drill_message(0, callback)

    def message(
        self,
        index: int,
        callback: Callable[[AssertablePromptMessage], Any] | None = None,
    ) -> AssertablePromptMessage | Self:
        return self._drill_message(index, callback)

    def last_message(
        self, callback: Callable[[AssertablePromptMessage], Any] | None = None
    ) -> AssertablePromptMessage | Self:
        return self._drill_message(-1, callback)

    def every_message(self, callback: Callable[[AssertablePromptMessage], Any]) -> Self:
        for idx, message in enumerate(self._messages()):
            if isinstance(message, dict):
                callback(AssertablePromptMessage(message, index=idx))
        return self

    def is_rejected_with_invalid_params(self) -> Self:
        error = self._require_error()
        if error.get("code") != -32602:
            raise AssertionError(
                f"Expected invalid-params (-32602) for prompt '{self._name}', got code={error.get('code')}"
            )
        return self

    def with_message_containing(self, substr: str) -> Self:
        error = self._require_error()
        message = error.get("message") or ""
        if substr not in message:
            raise AssertionError(f"Prompt '{self._name}' error message does not contain {substr!r}: {message!r}")
        return self
