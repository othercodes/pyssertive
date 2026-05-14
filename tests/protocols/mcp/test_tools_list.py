from __future__ import annotations

import pytest

from pyssertive.protocols.mcp import AssertableMCP


def _list_response(tools: list[dict], *, next_cursor: str | None = None) -> dict:
    result: dict = {"tools": tools}
    if next_cursor is not None:
        result["nextCursor"] = next_cursor
    return {"jsonrpc": "2.0", "id": 1, "result": result}


def test_lists_tools_should_pass_with_count():
    payload = _list_response([{"name": "a"}, {"name": "b"}, {"name": "c"}])
    AssertableMCP(payload).lists_tools().with_count(3)


def test_lists_tools_should_raise_when_count_mismatches():
    with pytest.raises(AssertionError, match="Expected 3 tools"):
        AssertableMCP(_list_response([{"name": "a"}])).lists_tools().with_count(3)


def test_lists_tools_should_raise_when_response_has_no_tools_list():
    payload = {"jsonrpc": "2.0", "id": 1, "result": {"other": []}}
    with pytest.raises(AssertionError, match="not a tools/list"):
        AssertableMCP(payload).lists_tools()


def test_contains_tool_should_pass_when_tool_present():
    payload = _list_response([{"name": "get_weather"}, {"name": "send_email"}])
    AssertableMCP(payload).lists_tools().contains_tool("get_weather")


def test_contains_tool_should_raise_when_tool_absent():
    payload = _list_response([{"name": "send_email"}])
    with pytest.raises(AssertionError, match="not found"):
        AssertableMCP(payload).lists_tools().contains_tool("get_weather")


def test_contains_tool_should_run_callback_for_inner_scope():
    payload = _list_response(
        [
            {
                "name": "get_weather",
                "description": "Look up current weather",
                "inputSchema": {
                    "type": "object",
                    "required": ["location"],
                    "properties": {"location": {"type": "string"}, "units": {"type": "string"}},
                },
                "outputSchema": {"type": "object"},
            }
        ]
    )
    AssertableMCP(payload).lists_tools().contains_tool(
        "get_weather",
        lambda t: t.documented().accepts(["location"]).accepts_optional(["units"]).has_output_schema(),
    )


def test_tool_def_documented_should_raise_when_description_missing():
    payload = _list_response([{"name": "x", "description": ""}])
    with pytest.raises(AssertionError, match="no description"):
        AssertableMCP(payload).lists_tools().contains_tool("x", lambda t: t.documented())


def test_tool_def_accepts_should_raise_when_required_param_missing():
    payload = _list_response([{"name": "x", "inputSchema": {"required": ["a"]}}])
    with pytest.raises(AssertionError, match="does not require parameters"):
        AssertableMCP(payload).lists_tools().contains_tool("x", lambda t: t.accepts(["b"]))


def test_tool_def_accepts_optional_should_raise_when_property_missing():
    payload = _list_response([{"name": "x", "inputSchema": {"properties": {"a": {}}}}])
    with pytest.raises(AssertionError, match="no input properties"):
        AssertableMCP(payload).lists_tools().contains_tool("x", lambda t: t.accepts_optional(["b"]))


def test_tool_def_has_output_schema_should_raise_when_field_absent():
    payload = _list_response([{"name": "x"}])
    with pytest.raises(AssertionError, match="no outputSchema"):
        AssertableMCP(payload).lists_tools().contains_tool("x", lambda t: t.has_output_schema())


def test_tool_def_does_not_accept_should_pass_when_params_absent():
    payload = _list_response([{"name": "x", "inputSchema": {"properties": {"a": {}}}}])
    AssertableMCP(payload).lists_tools().contains_tool("x", lambda t: t.does_not_accept(["b", "c"]))


def test_tool_def_does_not_accept_should_pass_when_no_input_schema():
    payload = _list_response([{"name": "x"}])
    AssertableMCP(payload).lists_tools().contains_tool("x", lambda t: t.does_not_accept(["any"]))


def test_tool_def_does_not_accept_should_raise_when_param_present():
    payload = _list_response([{"name": "x", "inputSchema": {"properties": {"internal": {}}}}])
    with pytest.raises(AssertionError, match=r"Tool 'x' should not expose properties \['internal'\]"):
        AssertableMCP(payload).lists_tools().contains_tool("x", lambda t: t.does_not_accept(["internal"]))


def test_tool_def_does_not_accept_should_return_self_for_chaining():
    payload = _list_response([{"name": "x", "description": "doc", "inputSchema": {"properties": {"a": {}}}}])
    AssertableMCP(payload).lists_tools().contains_tool("x", lambda t: t.does_not_accept(["forbidden"]).documented())


def test_does_not_contain_tool_should_pass_when_tool_absent():
    payload = _list_response([{"name": "send_email"}])
    AssertableMCP(payload).lists_tools().does_not_contain_tool("get_weather")


def test_does_not_contain_tool_should_raise_when_tool_present():
    payload = _list_response([{"name": "get_weather"}, {"name": "send_email"}])
    with pytest.raises(AssertionError, match="should not be in tools list"):
        AssertableMCP(payload).lists_tools().does_not_contain_tool("get_weather")


def test_lists_tools_has_more_pages_should_pass_when_next_cursor_present():
    payload = _list_response([{"name": "a"}], next_cursor="abc")
    AssertableMCP(payload).lists_tools().has_more_pages()


def test_lists_tools_has_more_pages_should_raise_when_next_cursor_absent():
    with pytest.raises(AssertionError, match="nextCursor"):
        AssertableMCP(_list_response([{"name": "a"}])).lists_tools().has_more_pages()


def test_every_tool_should_apply_callback_to_each_tool():
    payload = _list_response([{"name": "a"}, {"name": "b"}, {"name": "c"}])
    call_count = []
    AssertableMCP(payload).lists_tools().every_tool(lambda t: call_count.append(1))
    assert len(call_count) == 3


def test_every_tool_should_raise_with_tool_name_when_callback_fails():
    payload = _list_response(
        [
            {"name": "a", "description": "doc a"},
            {"name": "b"},
        ]
    )
    with pytest.raises(AssertionError, match="Tool 'b' has no description"):
        AssertableMCP(payload).lists_tools().every_tool(lambda t: t.documented())


def test_every_tool_should_pass_silently_when_tools_list_is_empty():
    AssertableMCP(_list_response([])).lists_tools().every_tool(lambda t: t.documented())


def test_every_tool_should_return_self_for_chaining():
    payload = _list_response([{"name": "a", "description": "doc a"}])
    AssertableMCP(payload).lists_tools().every_tool(lambda t: t.documented()).with_count(1)


def test_every_tool_should_skip_non_dict_items():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"tools": [{"name": "a"}, "not a dict", {"name": "b"}]},
    }
    call_count = []
    AssertableMCP(payload).lists_tools().every_tool(lambda t: call_count.append(1))
    assert len(call_count) == 2
