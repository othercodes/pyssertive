from __future__ import annotations

import pytest

from pyssertive.protocols.mcp import AssertableMCP


def _success_call(content: list[dict] | None = None, *, structured: dict | None = None, is_error: bool = False) -> dict:
    result: dict = {"content": content if content is not None else [{"type": "text", "text": "hello"}]}
    if is_error:
        result["isError"] = True
    if structured is not None:
        result["structuredContent"] = structured
    return {"jsonrpc": "2.0", "id": 1, "result": result}


def _error_call(code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": 1, "error": {"code": code, "message": message}}


def test_tool_succeeds_should_pass_when_response_is_successful():
    AssertableMCP(_success_call()).tool("get_weather").succeeds()


def test_tool_succeeds_should_raise_when_response_reports_tool_error():
    payload = _success_call(is_error=True, content=[{"type": "text", "text": "boom"}])
    with pytest.raises(AssertionError, match="isError=true"):
        AssertableMCP(payload).tool("x").succeeds()


def test_tool_returns_text_should_pass_when_text_block_matches():
    payload = _success_call(content=[{"type": "text", "text": "72°F"}])
    AssertableMCP(payload).tool("get_weather").returns_text("72°F")


def test_tool_returns_text_should_raise_when_no_text_block_matches():
    payload = _success_call(content=[{"type": "text", "text": "cold"}])
    with pytest.raises(AssertionError, match="did not return text"):
        AssertableMCP(payload).tool("get_weather").returns_text("72°F")


def test_tool_returns_text_containing_should_pass_when_substring_present():
    payload = _success_call(content=[{"type": "text", "text": "72°F partly cloudy"}])
    AssertableMCP(payload).tool("get_weather").returns_text_containing("partly")


def test_tool_returns_text_containing_should_raise_when_substring_absent():
    payload = _success_call(content=[{"type": "text", "text": "sunny"}])
    with pytest.raises(AssertionError, match="containing"):
        AssertableMCP(payload).tool("get_weather").returns_text_containing("rain")


def test_tool_returns_image_should_pass_when_image_block_present():
    payload = _success_call(content=[{"type": "image", "mimeType": "image/png", "data": "Zm9v"}])
    AssertableMCP(payload).tool("plot").returns_image()


def test_tool_returns_image_should_pass_when_mime_type_matches():
    payload = _success_call(content=[{"type": "image", "mimeType": "image/png", "data": "Zm9v"}])
    AssertableMCP(payload).tool("plot").returns_image(mime_type="image/png")


def test_tool_returns_image_should_raise_when_no_image_block_present():
    payload = _success_call(content=[{"type": "text", "text": "nope"}])
    with pytest.raises(AssertionError, match="did not return an image"):
        AssertableMCP(payload).tool("plot").returns_image()


def test_tool_returns_image_should_raise_when_mime_type_mismatches():
    payload = _success_call(content=[{"type": "image", "mimeType": "image/jpeg", "data": "Zm9v"}])
    with pytest.raises(AssertionError, match="mimeType"):
        AssertableMCP(payload).tool("plot").returns_image(mime_type="image/png")


def test_tool_returns_content_count_should_pass_when_count_matches():
    payload = _success_call(content=[{"type": "text", "text": "a"}, {"type": "text", "text": "b"}])
    AssertableMCP(payload).tool("multi").returns_content_count(2)


def test_tool_returns_content_count_should_raise_when_count_mismatches():
    with pytest.raises(AssertionError, match="content blocks"):
        AssertableMCP(_success_call()).tool("multi").returns_content_count(99)


def test_tool_returns_structured_should_pass_when_value_matches():
    payload = _success_call(structured={"temp": 72})
    AssertableMCP(payload).tool("get_weather").returns_structured({"temp": 72})


def test_tool_returns_structured_should_raise_when_value_differs():
    payload = _success_call(structured={"temp": 70})
    with pytest.raises(AssertionError, match="structuredContent"):
        AssertableMCP(payload).tool("get_weather").returns_structured({"temp": 72})


def test_tool_reports_tool_error_should_pass_when_is_error_flag_true():
    payload = _success_call(is_error=True, content=[{"type": "text", "text": "Invalid date"}])
    AssertableMCP(payload).tool("x").reports_tool_error()


def test_tool_reports_tool_error_should_raise_when_is_error_flag_absent():
    with pytest.raises(AssertionError, match="isError=true"):
        AssertableMCP(_success_call()).tool("x").reports_tool_error()


def test_tool_with_message_containing_should_pass_for_tool_error_messages():
    payload = _success_call(is_error=True, content=[{"type": "text", "text": "Invalid date format"}])
    AssertableMCP(payload).tool("x").reports_tool_error().with_message_containing("Invalid date")


def test_tool_with_message_containing_should_raise_when_text_does_not_contain_substring():
    payload = _success_call(is_error=True, content=[{"type": "text", "text": "Nope"}])
    with pytest.raises(AssertionError, match="does not contain"):
        AssertableMCP(payload).tool("x").reports_tool_error().with_message_containing("missing 'location'")


def test_tool_with_message_containing_should_pass_for_protocol_error_messages():
    payload = _error_call(-32602, "missing 'location'")
    AssertableMCP(payload).tool("x").is_rejected_with_invalid_params().with_message_containing("missing 'location'")


def test_tool_with_message_containing_should_raise_when_protocol_message_lacks_substring():
    payload = _error_call(-32602, "bad input")
    with pytest.raises(AssertionError, match="does not contain"):
        AssertableMCP(payload).tool("x").is_rejected_with_invalid_params().with_message_containing("missing")


def test_tool_is_rejected_as_unknown_tool_should_pass_for_method_not_found():
    payload = _error_call(-32601, "Method not found")
    AssertableMCP(payload).tool("unknown").is_rejected_as_unknown_tool()


def test_tool_is_rejected_as_unknown_tool_should_pass_for_invalid_params_with_unknown_tool_msg():
    payload = _error_call(-32602, "Unknown tool: foo")
    AssertableMCP(payload).tool("foo").is_rejected_as_unknown_tool()


def test_tool_is_rejected_as_unknown_tool_should_pass_for_invalid_params_with_not_found_msg():
    payload = _error_call(-32602, "Tool not found")
    AssertableMCP(payload).tool("foo").is_rejected_as_unknown_tool()


def test_tool_is_rejected_as_unknown_tool_should_raise_for_other_codes():
    payload = _error_call(-32603, "Internal")
    with pytest.raises(AssertionError, match="unknown-tool"):
        AssertableMCP(payload).tool("x").is_rejected_as_unknown_tool()


def test_tool_is_rejected_with_invalid_params_should_pass_for_minus_32602():
    payload = _error_call(-32602, "bad params")
    AssertableMCP(payload).tool("x").is_rejected_with_invalid_params()


def test_tool_is_rejected_with_invalid_params_should_raise_for_other_codes():
    payload = _error_call(-32601, "method missing")
    with pytest.raises(AssertionError, match="invalid-params"):
        AssertableMCP(payload).tool("x").is_rejected_with_invalid_params()


def test_tool_should_raise_when_calling_success_helper_on_error_response():
    payload = _error_call(-32602, "bad")
    with pytest.raises(AssertionError, match="protocol error"):
        AssertableMCP(payload).tool("x").succeeds()


def test_tool_should_raise_when_calling_error_helper_on_success_response():
    with pytest.raises(AssertionError, match="protocol-level error"):
        AssertableMCP(_success_call()).tool("x").is_rejected_as_unknown_tool()


def test_tool_succeeds_should_raise_when_result_is_missing():
    payload = {"jsonrpc": "2.0", "id": 1, "result": None}
    with pytest.raises(AssertionError, match="no result payload"):
        AssertableMCP(payload).tool("x").succeeds()


def test_tool_content_blocks_should_raise_when_content_is_not_a_list():
    payload = {"jsonrpc": "2.0", "id": 1, "result": {"content": "oops"}}
    with pytest.raises(AssertionError, match="no content list"):
        AssertableMCP(payload).tool("x").returns_text("hi")


def test_tool_content_blocks_should_raise_when_called_on_tool_error_response():
    payload = _success_call(is_error=True, content=[{"type": "text", "text": "boom"}])
    with pytest.raises(AssertionError, match="reports_tool_error"):
        AssertableMCP(payload).tool("x").returns_text("boom")


def test_tool_content_scope_should_pass_when_callback_validates_block():
    payload = _success_call(
        content=[{"type": "text", "text": "hi"}, {"type": "image", "mimeType": "image/png", "data": "Zm9v"}]
    )
    AssertableMCP(payload).tool("multi").content(0, lambda c: c.is_text().text_equals("hi"))


def test_tool_content_scope_should_raise_when_index_out_of_range():
    with pytest.raises(AssertionError, match="out of range"):
        AssertableMCP(_success_call()).tool("multi").content(99, lambda c: c.is_text())
