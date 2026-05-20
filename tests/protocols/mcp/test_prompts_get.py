from __future__ import annotations

import pytest

from pyssertive.protocols.mcp import AssertableMCP


def _get_response(messages: list[dict], *, description: str | None = None) -> dict:
    result: dict = {"messages": messages}
    if description is not None:
        result["description"] = description
    return {"jsonrpc": "2.0", "id": 1, "result": result}


def _error_call(code: int, message: str = "boom") -> dict:
    return {"jsonrpc": "2.0", "id": 1, "error": {"code": code, "message": message}}


def _user_text(text: str) -> dict:
    return {"role": "user", "content": {"type": "text", "text": text}}


def _assistant_text(text: str) -> dict:
    return {"role": "assistant", "content": {"type": "text", "text": text}}


# --- prompt(name) entry ---


def test_prompt_should_return_assertable_prompt_get():
    from pyssertive.protocols.mcp.prompts import AssertablePromptGet

    payload = _get_response([_user_text("hi")])
    result = AssertableMCP(payload).prompt("x")
    assert isinstance(result, AssertablePromptGet)


# --- with_description ---


def test_with_description_should_pass_when_matches():
    payload = _get_response([_user_text("hi")], description="A code review prompt")
    AssertableMCP(payload).prompt("x").with_description("A code review prompt")


def test_with_description_should_raise_when_differs():
    payload = _get_response([_user_text("hi")], description="other")
    with pytest.raises(AssertionError, match="description"):
        AssertableMCP(payload).prompt("x").with_description("expected")


def test_with_description_should_raise_when_absent():
    payload = _get_response([_user_text("hi")])
    with pytest.raises(AssertionError, match="description"):
        AssertableMCP(payload).prompt("x").with_description("expected")


def test_with_description_containing_should_pass_when_substring_present():
    payload = _get_response([_user_text("hi")], description="Reviews code for bugs and style")
    AssertableMCP(payload).prompt("x").with_description_containing("code for bugs")


def test_with_description_containing_should_raise_when_substring_absent():
    payload = _get_response([_user_text("hi")], description="other")
    with pytest.raises(AssertionError, match="does not contain"):
        AssertableMCP(payload).prompt("x").with_description_containing("missing")


def test_with_description_containing_should_raise_when_description_absent():
    payload = _get_response([_user_text("hi")])
    with pytest.raises(AssertionError, match="does not contain"):
        AssertableMCP(payload).prompt("x").with_description_containing("anything")


# --- with_message_count ---


def test_with_message_count_should_pass_when_count_matches():
    payload = _get_response([_user_text("a"), _assistant_text("b")])
    AssertableMCP(payload).prompt("x").with_message_count(2)


def test_with_message_count_should_raise_when_count_mismatches():
    with pytest.raises(AssertionError, match="2 messages"):
        AssertableMCP(_get_response([_user_text("a")])).prompt("x").with_message_count(2)


def test_with_message_count_should_raise_when_messages_field_absent():
    payload = {"jsonrpc": "2.0", "id": 1, "result": {"other": []}}
    with pytest.raises(AssertionError, match="messages"):
        AssertableMCP(payload).prompt("x").with_message_count(0)


# --- first_message / message / last_message (dual-mode) ---


def test_first_message_should_return_message_when_no_callback():
    from pyssertive.protocols.mcp.prompts import AssertablePromptMessage

    payload = _get_response([_user_text("hi"), _assistant_text("bye")])
    result = AssertableMCP(payload).prompt("x").first_message()
    assert isinstance(result, AssertablePromptMessage)


def test_first_message_should_invoke_callback_and_return_self():
    payload = _get_response([_user_text("hi"), _assistant_text("bye")])
    AssertableMCP(payload).prompt("x").first_message(lambda m: m.is_from_user()).with_message_count(2)


def test_first_message_chain_should_work_without_callback():
    payload = _get_response([_user_text("hi")])
    AssertableMCP(payload).prompt("x").first_message().is_from_user().content().is_not_empty()


def test_first_message_should_raise_when_messages_list_empty():
    payload = _get_response([])
    with pytest.raises(AssertionError, match="out of range"):
        AssertableMCP(payload).prompt("x").first_message()


def test_message_indexed_should_return_message_at_index():
    payload = _get_response([_user_text("a"), _assistant_text("b"), _user_text("c")])
    AssertableMCP(payload).prompt("x").message(1).is_from_assistant()


def test_message_indexed_should_raise_when_out_of_range():
    payload = _get_response([_user_text("a")])
    with pytest.raises(AssertionError, match="out of range"):
        AssertableMCP(payload).prompt("x").message(5)


def test_message_indexed_should_invoke_callback_and_return_self():
    payload = _get_response([_user_text("a"), _assistant_text("b")])
    AssertableMCP(payload).prompt("x").message(0, lambda m: m.is_from_user()).message(
        1, lambda m: m.is_from_assistant()
    )


def test_last_message_should_return_last_message():
    payload = _get_response([_user_text("a"), _assistant_text("b"), _user_text("c")])
    AssertableMCP(payload).prompt("x").last_message().is_from_user()


def test_last_message_should_invoke_callback_and_return_self():
    payload = _get_response([_user_text("a"), _assistant_text("b")])
    AssertableMCP(payload).prompt("x").last_message(lambda m: m.is_from_assistant()).with_message_count(2)


# --- every_message ---


def test_every_message_should_apply_callback_to_each_message():
    payload = _get_response([_user_text("a"), _user_text("b"), _user_text("c")])
    AssertableMCP(payload).prompt("x").every_message(lambda m: m.is_from_user())


def test_every_message_should_raise_with_index_when_callback_fails():
    payload = _get_response([_user_text("a"), _assistant_text("b")])
    with pytest.raises(AssertionError, match=r"Message\[1\]"):
        AssertableMCP(payload).prompt("x").every_message(lambda m: m.is_from_user())


def test_every_message_should_return_self_for_chaining():
    payload = _get_response([_user_text("a")])
    AssertableMCP(payload).prompt("x").every_message(lambda m: m.is_from_user()).with_message_count(1)


def test_every_message_should_skip_non_dict_items():
    payload = {"jsonrpc": "2.0", "id": 1, "result": {"messages": [_user_text("a"), "not a dict"]}}
    count: list[int] = []
    AssertableMCP(payload).prompt("x").every_message(lambda m: count.append(1))
    assert len(count) == 1


# --- AssertablePromptMessage: roles ---


def test_message_is_from_user_should_pass_when_role_user():
    payload = _get_response([_user_text("hi")])
    AssertableMCP(payload).prompt("x").first_message(lambda m: m.is_from_user())


def test_message_is_from_user_should_raise_when_role_assistant():
    payload = _get_response([_assistant_text("hi")])
    with pytest.raises(AssertionError, match="user"):
        AssertableMCP(payload).prompt("x").first_message(lambda m: m.is_from_user())


def test_message_is_from_assistant_should_pass_when_role_assistant():
    payload = _get_response([_assistant_text("hi")])
    AssertableMCP(payload).prompt("x").first_message(lambda m: m.is_from_assistant())


def test_message_is_from_assistant_should_raise_when_role_user():
    payload = _get_response([_user_text("hi")])
    with pytest.raises(AssertionError, match="assistant"):
        AssertableMCP(payload).prompt("x").first_message(lambda m: m.is_from_assistant())


# --- AssertablePromptMessage: content() dual-mode ---


def test_message_content_should_return_assertable_content_when_no_callback():
    from pyssertive.protocols.mcp.content import AssertableContent

    payload = _get_response([_user_text("hi")])
    result = AssertableMCP(payload).prompt("x").first_message().content()
    assert isinstance(result, AssertableContent)


def test_message_content_chain_should_work_without_callback():
    payload = _get_response([_user_text("hi")])
    AssertableMCP(payload).prompt("x").first_message().content().is_text().with_text("hi")


def test_message_content_should_invoke_callback_and_return_self():
    payload = _get_response([_user_text("hi")])
    AssertableMCP(payload).prompt("x").first_message(lambda m: m.content(lambda c: c.is_text().with_text("hi")))


def test_message_should_raise_when_message_is_not_a_dict():
    payload = {"jsonrpc": "2.0", "id": 1, "result": {"messages": ["not-a-dict"]}}
    with pytest.raises(AssertionError, match="is not a dict"):
        AssertableMCP(payload).prompt("x").first_message().is_from_user()


@pytest.mark.parametrize(
    ("message", "match"),
    [
        ({"role": "user", "content": "not-a-dict"}, "content is not a dict"),
        ({"role": "user"}, "no 'content' field"),
    ],
    ids=["content_wrong_type", "content_absent"],
)
def test_message_content_should_raise_when_content_field_invalid(message, match):
    payload = _get_response([message])
    with pytest.raises(AssertionError, match=match):
        AssertableMCP(payload).prompt("x").first_message().content()


def test_prompt_should_raise_when_envelope_has_no_result_payload():
    payload = {"jsonrpc": "2.0", "id": 1, "result": None}
    with pytest.raises(AssertionError, match="no result payload"):
        AssertableMCP(payload).prompt("x").with_message_count(0)


# --- protocol error path ---


def test_prompt_is_rejected_with_invalid_params_should_pass_when_code_minus_32602():
    AssertableMCP(_error_call(-32602, "bad args")).prompt("x").is_rejected_with_invalid_params()


def test_prompt_is_rejected_with_invalid_params_should_raise_for_other_codes():
    with pytest.raises(AssertionError, match="invalid-params"):
        AssertableMCP(_error_call(-32601)).prompt("x").is_rejected_with_invalid_params()


def test_prompt_with_message_containing_should_pass_when_protocol_message_contains_substring():
    payload = _error_call(-32602, "Missing required 'code' argument")
    AssertableMCP(payload).prompt("x").is_rejected_with_invalid_params().with_message_containing("Missing required")


def test_prompt_with_message_containing_should_raise_when_substring_absent():
    payload = _error_call(-32602, "bad args")
    with pytest.raises(AssertionError, match="does not contain"):
        AssertableMCP(payload).prompt("x").is_rejected_with_invalid_params().with_message_containing("missing")


def test_prompt_should_raise_when_calling_success_helper_on_error_response():
    payload = _error_call(-32602, "bad")
    with pytest.raises(AssertionError, match="protocol error"):
        AssertableMCP(payload).prompt("x").with_message_count(1)


def test_prompt_succeeds_should_pass_when_result_present():
    payload = _get_response([_user_text("hi")])
    AssertableMCP(payload).prompt("x").succeeds()


def test_prompt_succeeds_should_raise_when_error_envelope():
    with pytest.raises(AssertionError, match="protocol error"):
        AssertableMCP(_error_call(-32602)).prompt("x").succeeds()


def test_prompt_succeeds_should_chain_back_to_self():
    payload = _get_response([_user_text("hi")])
    AssertableMCP(payload).prompt("x").succeeds().with_message_count(1)


def test_prompt_should_raise_when_calling_error_helper_on_success_response():
    with pytest.raises(AssertionError, match="protocol-level error"):
        AssertableMCP(_get_response([_user_text("hi")])).prompt("x").is_rejected_with_invalid_params()
