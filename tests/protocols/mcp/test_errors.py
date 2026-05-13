from __future__ import annotations

import pytest

from pyssertive.protocols.mcp import AssertableMCP, ErrorCode
from pyssertive.protocols.mcp.errors import describe


def _err(code: int, message: str = "boom") -> dict:
    return {"jsonrpc": "2.0", "id": 1, "error": {"code": code, "message": message}}


@pytest.mark.parametrize(
    ("helper", "code"),
    [
        ("is_rejected_as_parse_error", ErrorCode.PARSE_ERROR),
        ("is_rejected_as_invalid_request", ErrorCode.INVALID_REQUEST),
        ("is_rejected_as_method_not_found", ErrorCode.METHOD_NOT_FOUND),
        ("is_rejected_with_invalid_params", ErrorCode.INVALID_PARAMS),
        ("is_rejected_as_internal_error", ErrorCode.INTERNAL_ERROR),
        ("is_rejected_as_resource_not_found", ErrorCode.RESOURCE_NOT_FOUND),
        ("is_rejected_as_user_rejected", ErrorCode.USER_REJECTED),
    ],
)
def test_error_helper_should_pass_when_code_matches(helper: str, code: ErrorCode):
    getattr(AssertableMCP(_err(int(code))), helper)()


@pytest.mark.parametrize(
    "helper",
    [
        "is_rejected_as_parse_error",
        "is_rejected_as_invalid_request",
        "is_rejected_as_method_not_found",
        "is_rejected_with_invalid_params",
        "is_rejected_as_internal_error",
        "is_rejected_as_resource_not_found",
        "is_rejected_as_user_rejected",
    ],
)
def test_error_helper_should_raise_when_envelope_is_success(helper: str):
    payload = {"jsonrpc": "2.0", "id": 1, "result": {}}
    with pytest.raises(AssertionError, match="got success"):
        getattr(AssertableMCP(payload), helper)()


def test_error_helper_should_raise_when_code_mismatches():
    payload = _err(-32700)
    with pytest.raises(AssertionError, match="Expected error code -32601"):
        AssertableMCP(payload).is_rejected_as_method_not_found()


def test_because_message_contains_should_pass_when_substring_present():
    AssertableMCP(_err(-32602, "missing 'location'")).is_rejected_with_invalid_params().because_message_contains(
        "missing"
    )


def test_because_message_contains_should_raise_when_substring_absent():
    with pytest.raises(AssertionError, match="does not contain"):
        AssertableMCP(_err(-32602, "bad input")).is_rejected_with_invalid_params().because_message_contains("missing")


def test_because_message_contains_should_raise_when_envelope_has_no_error():
    payload = {"jsonrpc": "2.0", "id": 1, "result": {}}
    with pytest.raises(AssertionError, match="requires an error envelope"):
        AssertableMCP(payload).because_message_contains("anything")


def test_describe_should_return_human_readable_label_for_known_codes():
    assert describe(-32601) == "method not found"
    assert describe(-32002) == "resource not found"


def test_describe_should_fall_back_to_code_for_unknown_values():
    assert describe(-99999) == "code -99999"
