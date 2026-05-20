from __future__ import annotations

import json

import pytest

from pyssertive.protocols.mcp import AssertableMCP


def _success(result: dict | None = None) -> dict:
    return {"jsonrpc": "2.0", "id": 1, "result": result or {"ok": True}}


def _error(code: int = -32601, message: str = "Method not found") -> dict:
    return {"jsonrpc": "2.0", "id": 1, "error": {"code": code, "message": message}}


class _FakeResponse:
    def __init__(self, content: bytes, headers: dict[str, str]) -> None:
        self.content = content
        self.headers = headers


def test_assertable_mcp_should_accept_dict_payload():
    AssertableMCP(_success())


def test_assertable_mcp_should_accept_bytes_payload():
    AssertableMCP(json.dumps(_success()).encode("utf-8"))


def test_assertable_mcp_should_accept_str_payload():
    AssertableMCP(json.dumps(_success()))


def test_assertable_mcp_should_unwrap_sse_when_body_starts_with_data_line():
    sse = 'data: {"jsonrpc": "2.0", "id": 1, "result": {}}\n\n'
    AssertableMCP(sse)


def test_assertable_mcp_should_unwrap_sse_when_body_starts_with_event_line():
    sse = 'event: message\ndata: {"jsonrpc": "2.0", "id": 1, "result": {"ok": true}}\n\n'
    AssertableMCP(sse)


def test_assertable_mcp_should_raise_when_sse_frame_has_no_data_line():
    response = _FakeResponse(b"event: ping\n: keep-alive\n\n", {"Content-Type": "text/event-stream"})
    with pytest.raises(AssertionError, match="no `data:` line"):
        AssertableMCP(response)


def test_assertable_mcp_should_accept_response_like_object_with_content_and_headers():
    response = _FakeResponse(json.dumps(_success()).encode(), {"Content-Type": "application/json"})
    AssertableMCP(response)


def test_assertable_mcp_should_auto_detect_sse_from_response_headers():
    body = 'data: {"jsonrpc": "2.0", "id": 1, "result": {"x": 1}}\n\n'
    response = _FakeResponse(body.encode(), {"Content-Type": "text/event-stream"})
    AssertableMCP(response)


def test_assertable_mcp_should_handle_response_with_lowercase_content_type_header():
    body = 'data: {"jsonrpc": "2.0", "id": 1, "result": {}}\n\n'
    response = _FakeResponse(body.encode(), {"content-type": "text/event-stream"})
    AssertableMCP(response)


def test_assertable_mcp_should_fall_back_when_headers_object_has_no_get():
    class _WeirdHeaders:
        pass

    class _WeirdResponse:
        content = json.dumps(_success()).encode("utf-8")
        headers = _WeirdHeaders()

    AssertableMCP(_WeirdResponse())


def test_assertable_mcp_should_raise_when_payload_is_not_a_dict():
    with pytest.raises(AssertionError, match="must be a JSON object"):
        AssertableMCP("[1, 2, 3]")


def test_assertable_mcp_should_raise_when_jsonrpc_marker_missing():
    with pytest.raises(AssertionError, match="missing required 'jsonrpc'"):
        AssertableMCP({"id": 1, "result": {}})


def test_assertable_mcp_should_raise_for_malformed_json():
    with pytest.raises(AssertionError, match="not valid JSON"):
        AssertableMCP("{not json")


def test_assertable_mcp_should_raise_for_unsupported_payload_type():
    with pytest.raises(AssertionError, match="Unsupported payload type"):
        AssertableMCP(12345)


def test_assertable_mcp_should_detect_error_response_with_code_and_message():
    AssertableMCP(_error(code=-32602, message="Bad params")).is_rejected_with_invalid_params().because_message_contains(
        "Bad"
    )


def test_assertable_mcp_should_treat_error_with_missing_code_as_no_match():
    payload = {"jsonrpc": "2.0", "id": 1, "error": {"message": "no code"}}
    with pytest.raises(AssertionError, match="Expected error code"):
        AssertableMCP(payload).is_rejected_with_invalid_params()


def test_assertable_mcp_should_treat_invalid_error_field_as_no_error():
    payload = {"jsonrpc": "2.0", "id": 1, "error": "boom"}
    with pytest.raises(AssertionError, match="Expected error code"):
        AssertableMCP(payload).is_rejected_with_invalid_params()


def test_assertable_mcp_should_return_empty_message_when_error_absent_for_because_message():
    with pytest.raises(AssertionError, match="requires an error envelope"):
        AssertableMCP(_success()).because_message_contains("anything")


def test_assertable_mcp_should_return_empty_message_when_error_field_is_not_a_dict():
    payload = {"jsonrpc": "2.0", "id": 1, "error": "boom"}
    with pytest.raises(AssertionError, match="does not contain"):
        AssertableMCP(payload).because_message_contains("anything")


def test_is_rejected_with_code_should_pass_when_code_matches():
    AssertableMCP(_error(code=-32001, message="Auth failed")).is_rejected_with_code(-32001)


def test_is_rejected_with_code_should_raise_when_code_differs():
    with pytest.raises(AssertionError, match="Expected error code -32001"):
        AssertableMCP(_error(code=-32602, message="Bad params")).is_rejected_with_code(-32001)


def test_is_rejected_with_code_should_raise_when_no_error_envelope():
    with pytest.raises(AssertionError, match="got success"):
        AssertableMCP(_success()).is_rejected_with_code(-32001)


def test_because_message_equals_should_pass_when_exact_match():
    AssertableMCP(_error(message="Missing Authorization header")).because_message_equals("Missing Authorization header")


def test_because_message_equals_should_raise_when_message_differs():
    with pytest.raises(AssertionError, match="Error message does not match"):
        AssertableMCP(_error(message="actual")).because_message_equals("expected")


def test_because_message_equals_should_raise_when_no_error_envelope():
    with pytest.raises(AssertionError, match="requires an error envelope"):
        AssertableMCP(_success()).because_message_equals("anything")


def test_is_prompts_list_changed_notification_should_pass_when_method_matches_and_no_id():
    payload = {"jsonrpc": "2.0", "method": "notifications/prompts/list_changed"}
    AssertableMCP(payload).is_prompts_list_changed_notification()


def test_is_prompts_list_changed_notification_should_raise_when_method_differs():
    payload = {"jsonrpc": "2.0", "method": "notifications/tools/list_changed"}
    with pytest.raises(AssertionError, match="notifications/prompts/list_changed"):
        AssertableMCP(payload).is_prompts_list_changed_notification()


def test_is_prompts_list_changed_notification_should_raise_when_envelope_has_id():
    payload = {"jsonrpc": "2.0", "id": 1, "method": "notifications/prompts/list_changed"}
    with pytest.raises(AssertionError, match="no 'id' field"):
        AssertableMCP(payload).is_prompts_list_changed_notification()


def test_is_prompts_list_changed_notification_should_raise_when_method_absent():
    payload = {"jsonrpc": "2.0", "result": {}}
    with pytest.raises(AssertionError, match="notifications/prompts/list_changed"):
        AssertableMCP(payload).is_prompts_list_changed_notification()
