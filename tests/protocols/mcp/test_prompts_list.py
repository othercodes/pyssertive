from __future__ import annotations

import pytest

from pyssertive.protocols.mcp import AssertableMCP


def _list_response(prompts: list[dict], *, next_cursor: str | None = None) -> dict:
    result: dict = {"prompts": prompts}
    if next_cursor is not None:
        result["nextCursor"] = next_cursor
    return {"jsonrpc": "2.0", "id": 1, "result": result}


# --- entry point + count ---


def test_lists_prompts_should_pass_with_count():
    payload = _list_response([{"name": "a"}, {"name": "b"}, {"name": "c"}])
    AssertableMCP(payload).lists_prompts().with_count(3)


def test_lists_prompts_should_raise_when_count_mismatches():
    with pytest.raises(AssertionError, match="Expected 3 prompts"):
        AssertableMCP(_list_response([{"name": "a"}])).lists_prompts().with_count(3)


def test_lists_prompts_should_raise_when_response_has_no_prompts_list():
    payload = {"jsonrpc": "2.0", "id": 1, "result": {"other": []}}
    with pytest.raises(AssertionError, match="not a prompts/list"):
        AssertableMCP(payload).lists_prompts()


# --- contains_prompt ---


def test_contains_prompt_should_pass_when_prompt_present():
    payload = _list_response([{"name": "code_review"}, {"name": "summarize"}])
    AssertableMCP(payload).lists_prompts().contains_prompt("code_review")


def test_contains_prompt_should_raise_when_prompt_absent():
    payload = _list_response([{"name": "summarize"}])
    with pytest.raises(AssertionError, match="not found"):
        AssertableMCP(payload).lists_prompts().contains_prompt("code_review")


def test_contains_prompt_should_run_callback_for_inner_scope():
    payload = _list_response(
        [
            {
                "name": "code_review",
                "description": "Review code for bugs",
                "arguments": [
                    {"name": "code", "required": True},
                    {"name": "language", "required": False},
                ],
            }
        ]
    )
    AssertableMCP(payload).lists_prompts().contains_prompt(
        "code_review",
        lambda p: p.documented().accepts(["code"]).accepts_optional(["language"]),
    )


# --- AssertablePromptDef ---


def test_prompt_def_documented_should_pass_when_description_present():
    payload = _list_response([{"name": "x", "description": "doc"}])
    AssertableMCP(payload).lists_prompts().contains_prompt("x", lambda p: p.documented())


def test_prompt_def_documented_should_raise_when_description_missing():
    payload = _list_response([{"name": "x"}])
    with pytest.raises(AssertionError, match="no description"):
        AssertableMCP(payload).lists_prompts().contains_prompt("x", lambda p: p.documented())


def test_prompt_def_documented_should_raise_when_description_empty():
    payload = _list_response([{"name": "x", "description": ""}])
    with pytest.raises(AssertionError, match="no description"):
        AssertableMCP(payload).lists_prompts().contains_prompt("x", lambda p: p.documented())


def test_prompt_def_accepts_should_pass_when_required_argument_present():
    payload = _list_response([{"name": "x", "arguments": [{"name": "code", "required": True}]}])
    AssertableMCP(payload).lists_prompts().contains_prompt("x", lambda p: p.accepts(["code"]))


def test_prompt_def_accepts_should_raise_when_required_argument_missing():
    payload = _list_response([{"name": "x", "arguments": [{"name": "other", "required": True}]}])
    with pytest.raises(AssertionError, match="does not require arguments"):
        AssertableMCP(payload).lists_prompts().contains_prompt("x", lambda p: p.accepts(["code"]))


def test_prompt_def_accepts_should_raise_when_argument_present_but_optional():
    payload = _list_response([{"name": "x", "arguments": [{"name": "code", "required": False}]}])
    with pytest.raises(AssertionError, match="does not require arguments"):
        AssertableMCP(payload).lists_prompts().contains_prompt("x", lambda p: p.accepts(["code"]))


def test_prompt_def_accepts_optional_should_pass_when_optional_argument_present():
    payload = _list_response([{"name": "x", "arguments": [{"name": "language", "required": False}]}])
    AssertableMCP(payload).lists_prompts().contains_prompt("x", lambda p: p.accepts_optional(["language"]))


def test_prompt_def_accepts_optional_should_raise_when_argument_missing():
    payload = _list_response([{"name": "x", "arguments": [{"name": "code", "required": True}]}])
    with pytest.raises(AssertionError, match="no optional arguments"):
        AssertableMCP(payload).lists_prompts().contains_prompt("x", lambda p: p.accepts_optional(["language"]))


def test_prompt_def_accepts_optional_should_raise_when_argument_marked_required():
    payload = _list_response([{"name": "x", "arguments": [{"name": "language", "required": True}]}])
    with pytest.raises(AssertionError, match="no optional arguments"):
        AssertableMCP(payload).lists_prompts().contains_prompt("x", lambda p: p.accepts_optional(["language"]))


def test_prompt_def_does_not_accept_should_pass_when_arguments_absent():
    payload = _list_response([{"name": "x", "arguments": [{"name": "code", "required": True}]}])
    AssertableMCP(payload).lists_prompts().contains_prompt("x", lambda p: p.does_not_accept(["password", "token"]))


def test_prompt_def_does_not_accept_should_pass_when_no_arguments_array():
    payload = _list_response([{"name": "x"}])
    AssertableMCP(payload).lists_prompts().contains_prompt("x", lambda p: p.does_not_accept(["any"]))


def test_prompt_def_does_not_accept_should_raise_when_forbidden_argument_present():
    payload = _list_response([{"name": "x", "arguments": [{"name": "password", "required": True}]}])
    with pytest.raises(AssertionError, match=r"Prompt 'x' should not expose arguments \['password'\]"):
        AssertableMCP(payload).lists_prompts().contains_prompt("x", lambda p: p.does_not_accept(["password"]))


def test_prompt_def_methods_should_return_self_for_chaining():
    payload = _list_response(
        [
            {
                "name": "x",
                "description": "doc",
                "arguments": [{"name": "code", "required": True}],
            }
        ]
    )
    AssertableMCP(payload).lists_prompts().contains_prompt(
        "x",
        lambda p: p.documented().accepts(["code"]).does_not_accept(["password"]),
    )


# --- does_not_contain_prompt ---


def test_does_not_contain_prompt_should_pass_when_absent():
    payload = _list_response([{"name": "summarize"}])
    AssertableMCP(payload).lists_prompts().does_not_contain_prompt("code_review")


def test_does_not_contain_prompt_should_raise_when_present():
    payload = _list_response([{"name": "code_review"}, {"name": "summarize"}])
    with pytest.raises(AssertionError, match="should not be in prompts list"):
        AssertableMCP(payload).lists_prompts().does_not_contain_prompt("code_review")


# --- has_more_pages ---


def test_lists_prompts_has_more_pages_should_pass_when_next_cursor_present():
    payload = _list_response([{"name": "a"}], next_cursor="abc")
    AssertableMCP(payload).lists_prompts().has_more_pages()


def test_lists_prompts_has_more_pages_should_raise_when_next_cursor_absent():
    with pytest.raises(AssertionError, match="nextCursor"):
        AssertableMCP(_list_response([{"name": "a"}])).lists_prompts().has_more_pages()


# --- every_prompt ---


def test_every_prompt_should_apply_callback_to_each_prompt():
    payload = _list_response([{"name": "a"}, {"name": "b"}, {"name": "c"}])
    call_count: list[int] = []
    AssertableMCP(payload).lists_prompts().every_prompt(lambda p: call_count.append(1))
    assert len(call_count) == 3


def test_every_prompt_should_raise_with_prompt_name_when_callback_fails():
    payload = _list_response(
        [
            {"name": "a", "description": "doc a"},
            {"name": "b"},
        ]
    )
    with pytest.raises(AssertionError, match="Prompt 'b' has no description"):
        AssertableMCP(payload).lists_prompts().every_prompt(lambda p: p.documented())


def test_every_prompt_should_pass_silently_when_list_is_empty():
    AssertableMCP(_list_response([])).lists_prompts().every_prompt(lambda p: p.documented())


def test_every_prompt_should_return_self_for_chaining():
    payload = _list_response([{"name": "a", "description": "doc a"}])
    AssertableMCP(payload).lists_prompts().every_prompt(lambda p: p.documented()).with_count(1)


def test_every_prompt_should_skip_non_dict_items():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"prompts": [{"name": "a"}, "not a dict", {"name": "b"}]},
    }
    call_count: list[int] = []
    AssertableMCP(payload).lists_prompts().every_prompt(lambda p: call_count.append(1))
    assert len(call_count) == 2
