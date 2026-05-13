from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

from pyssertive.protocols.mcp.errors import ErrorCode, describe
from pyssertive.protocols.mcp.tools import AssertableToolCall, AssertableToolList


def _decode_sse(body: str) -> str:
    for line in body.splitlines():
        if line.startswith("data:"):
            return line[5:].lstrip()
    raise AssertionError(f"SSE frame contained no `data:` line: {body[:200]!r}")


def _coerce_to_text(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, (bytes, bytearray)):
        return payload.decode("utf-8")
    raise AssertionError(f"Unsupported payload type for MCP envelope: {type(payload).__name__}")


def _looks_like_sse(text: str, *, content_type: str | None) -> bool:
    if content_type and "text/event-stream" in content_type.lower():
        return True
    return text.lstrip().startswith(("event:", "data:", ":"))


@dataclass(frozen=True)
class _Envelope:
    raw: dict[str, Any]

    @property
    def is_success(self) -> bool:
        return "result" in self.raw and "error" not in self.raw

    @property
    def has_error(self) -> bool:
        return "error" in self.raw

    @property
    def result(self) -> Any:
        return self.raw.get("result")

    @property
    def error(self) -> dict[str, Any] | None:
        err = self.raw.get("error")
        return err if isinstance(err, dict) else None

    @property
    def error_code(self) -> int | None:
        error = self.error
        if error is None:
            return None
        code = error.get("code")
        return code if isinstance(code, int) else None

    @property
    def error_message(self) -> str:
        error = self.error
        if error is None:
            return ""
        msg = error.get("message")
        return msg if isinstance(msg, str) else ""


def _parse_text(text: str, *, content_type: str | None) -> _Envelope:
    body = _decode_sse(text) if _looks_like_sse(text, content_type=content_type) else text
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"MCP payload is not valid JSON: {exc.msg}") from exc
    return _validate_and_wrap(data)


def _validate_and_wrap(data: Any) -> _Envelope:
    if not isinstance(data, dict):
        raise AssertionError(f"MCP envelope must be a JSON object, got {type(data).__name__}")
    if data.get("jsonrpc") != "2.0":
        raise AssertionError("MCP envelope missing required 'jsonrpc': '2.0' marker")
    return _Envelope(raw=data)


class AssertableMCP:
    def __init__(self, payload: Any) -> None:
        if isinstance(payload, dict):
            self._envelope = _validate_and_wrap(payload)
        elif (
            hasattr(payload, "content")
            and hasattr(payload, "headers")
            and not isinstance(payload, (bytes, bytearray, str))
        ):
            headers = payload.headers
            try:
                ct = headers.get("Content-Type") or headers.get("content-type")
            except AttributeError:
                ct = None
            self._envelope = _parse_text(_coerce_to_text(payload.content), content_type=ct)
        else:
            self._envelope = _parse_text(_coerce_to_text(payload), content_type=None)

    def _require_result(self) -> dict[str, Any]:
        if not self._envelope.is_success:
            raise AssertionError(
                f"Expected MCP success response, got error: code={self._envelope.error_code} "
                f"message={self._envelope.error_message!r}"
            )
        result = self._envelope.result
        if not isinstance(result, dict):
            raise AssertionError(f"MCP result is not an object: {result!r}")
        return result

    def _capabilities(self) -> dict[str, Any]:
        caps = self._require_result().get("capabilities")
        if not isinstance(caps, dict):
            raise AssertionError("Initialize response has no 'capabilities' object")
        return caps

    def negotiated_protocol(self, expected: str) -> Self:
        actual = self._require_result().get("protocolVersion")
        if actual != expected:
            raise AssertionError(f"Expected protocolVersion {expected!r}, got {actual!r}")
        return self

    def server_named(self, expected: str) -> Self:
        info = self._require_result().get("serverInfo") or {}
        actual = info.get("name")
        if actual != expected:
            raise AssertionError(f"Expected serverInfo.name {expected!r}, got {actual!r}")
        return self

    def server_version(self, expected: str) -> Self:
        info = self._require_result().get("serverInfo") or {}
        actual = info.get("version")
        if actual != expected:
            raise AssertionError(f"Expected serverInfo.version {expected!r}, got {actual!r}")
        return self

    def supports_tools(self) -> Self:
        if "tools" not in self._capabilities():
            raise AssertionError("Server does not advertise 'tools' capability")
        return self

    def supports_resources(self, *, subscribe: bool | None = None) -> Self:
        caps = self._capabilities()
        if "resources" not in caps:
            raise AssertionError("Server does not advertise 'resources' capability")
        if subscribe is not None:
            actual = bool((caps.get("resources") or {}).get("subscribe"))
            if actual != subscribe:
                raise AssertionError(f"Expected resources.subscribe={subscribe}, got {actual}")
        return self

    def supports_prompts(self) -> Self:
        if "prompts" not in self._capabilities():
            raise AssertionError("Server does not advertise 'prompts' capability")
        return self

    def supports_logging(self) -> Self:
        if "logging" not in self._capabilities():
            raise AssertionError("Server does not advertise 'logging' capability")
        return self

    def has_instructions(self) -> Self:
        if not self._require_result().get("instructions"):
            raise AssertionError("Initialize response has no instructions text")
        return self

    def lists_tools(self) -> AssertableToolList:
        return AssertableToolList(self._require_result())

    def tool(self, name: str) -> AssertableToolCall:
        return AssertableToolCall(
            name=name,
            result=self._envelope.result if self._envelope.is_success else None,
            error=self._envelope.error if self._envelope.has_error else None,
        )

    def _expect_error_code(self, expected: ErrorCode) -> Self:
        if not self._envelope.has_error:
            raise AssertionError(f"Expected MCP error response ({describe(expected)}), got success")
        actual = self._envelope.error_code
        if actual != int(expected):
            raise AssertionError(f"Expected error code {int(expected)} ({describe(expected)}), got {actual}")
        return self

    def is_rejected_as_parse_error(self) -> Self:
        return self._expect_error_code(ErrorCode.PARSE_ERROR)

    def is_rejected_as_invalid_request(self) -> Self:
        return self._expect_error_code(ErrorCode.INVALID_REQUEST)

    def is_rejected_as_method_not_found(self) -> Self:
        return self._expect_error_code(ErrorCode.METHOD_NOT_FOUND)

    def is_rejected_with_invalid_params(self) -> Self:
        return self._expect_error_code(ErrorCode.INVALID_PARAMS)

    def is_rejected_as_internal_error(self) -> Self:
        return self._expect_error_code(ErrorCode.INTERNAL_ERROR)

    def is_rejected_as_resource_not_found(self) -> Self:
        return self._expect_error_code(ErrorCode.RESOURCE_NOT_FOUND)

    def is_rejected_as_user_rejected(self) -> Self:
        return self._expect_error_code(ErrorCode.USER_REJECTED)

    def because_message_contains(self, substr: str) -> Self:
        if not self._envelope.has_error:
            raise AssertionError("because_message_contains() requires an error envelope")
        message = self._envelope.error_message
        if substr not in message:
            raise AssertionError(f"Error message does not contain {substr!r}: {message!r}")
        return self
