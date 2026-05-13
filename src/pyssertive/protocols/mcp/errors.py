from __future__ import annotations

from enum import IntEnum


class ErrorCode(IntEnum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    RESOURCE_NOT_FOUND = -32002
    USER_REJECTED = -1


_ERROR_LABELS = {
    ErrorCode.PARSE_ERROR: "parse error",
    ErrorCode.INVALID_REQUEST: "invalid request",
    ErrorCode.METHOD_NOT_FOUND: "method not found",
    ErrorCode.INVALID_PARAMS: "invalid params",
    ErrorCode.INTERNAL_ERROR: "internal error",
    ErrorCode.RESOURCE_NOT_FOUND: "resource not found",
    ErrorCode.USER_REJECTED: "user rejected",
}


def describe(code: int) -> str:
    try:
        return _ERROR_LABELS[ErrorCode(code)]
    except ValueError:
        return f"code {code}"
