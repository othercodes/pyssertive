from __future__ import annotations

from pathlib import Path

import pytest

from pyssertive.formats.json import AssertableJson
from tests.adapters._factories import _make_django_response, _make_httpx_response, _pair

JSON_RESPONSE_FACTORIES = _pair(
    lambda body, status=200: _make_django_response(body, status=status, content_type="application/json"),
    lambda body, status=200: _make_httpx_response(body, status=status, content_type="application/json"),
)

SCHEMAS_DIR = Path(__file__).resolve().parents[1] / "schemas"

SIMPLE = {"ok": True}
LIST_BODY = {"items": [{"id": 1}, {"id": 2}, {"id": 3}]}
ARRAY_BODY = [{"id": 1}, {"id": 2}]
NESTED = {
    "user": {"id": 1, "name": "John", "profile": {"age": 30, "city": "NYC"}},
    "tags": ["python", "django"],
    "count": 42,
}


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_should_return_assertable_json_when_no_arguments(make_response):
    response = make_response(SIMPLE)
    assert isinstance(response.assert_json(), AssertableJson)


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_should_raise_when_payload_is_invalid(make_response):
    response = make_response("not valid json")
    with pytest.raises(AssertionError, match="not valid JSON"):
        response.assert_json()


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_path_should_pass_when_value_matches_at_path(make_response):
    response = make_response(SIMPLE)
    assert response.assert_json_path("ok", True) is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_path_should_resolve_nested_paths(make_response):
    response = make_response(LIST_BODY)
    assert response.assert_json_path("items.0.id", 1) is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_path_should_raise_when_value_mismatches(make_response):
    response = make_response(SIMPLE)
    with pytest.raises(AssertionError, match="Expected"):
        response.assert_json_path("ok", False)


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_path_should_raise_when_path_absent(make_response):
    response = make_response(SIMPLE)
    with pytest.raises(AssertionError, match="not found"):
        response.assert_json_path("missing.path", True)


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_fragment_should_pass_when_fragment_is_subset(make_response):
    response = make_response(SIMPLE)
    assert response.assert_json_fragment({"ok": True}) is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_fragment_should_raise_when_fragment_absent(make_response):
    response = make_response(SIMPLE)
    with pytest.raises(AssertionError, match="not found"):
        response.assert_json_fragment({"missing": "value"})


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_missing_fragment_should_pass_when_fragment_absent(make_response):
    response = make_response(SIMPLE)
    assert response.assert_json_missing_fragment({"missing": "value"}) is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_missing_fragment_should_raise_when_fragment_present(make_response):
    response = make_response(SIMPLE)
    with pytest.raises(AssertionError, match="Unexpected fragment"):
        response.assert_json_missing_fragment({"ok": True})


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_count_should_pass_when_count_matches_at_path(make_response):
    response = make_response(LIST_BODY)
    assert response.assert_json_count(3, path="items") is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_count_should_apply_at_root_when_no_path_given(make_response):
    response = make_response(LIST_BODY)
    assert response.assert_json_count(1) is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_count_should_raise_when_count_mismatches(make_response):
    response = make_response(LIST_BODY)
    with pytest.raises(AssertionError, match="Expected"):
        response.assert_json_count(10, path="items")


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_count_should_raise_when_value_is_not_countable(make_response):
    response = make_response(SIMPLE)
    with pytest.raises(AssertionError, match="countable"):
        response.assert_json_count(1, path="ok")


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_exact_json_should_pass_when_payload_matches_full_value(make_response):
    response = make_response(SIMPLE)
    assert response.assert_exact_json({"ok": True}) is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_exact_json_should_raise_when_payload_differs(make_response):
    response = make_response(SIMPLE)
    with pytest.raises(AssertionError, match="Expected exact JSON"):
        response.assert_exact_json({"ok": True, "extra": "field"})


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_structure_should_pass_when_keys_and_types_match(make_response):
    response = make_response(NESTED)
    assert response.assert_json_structure({"user": dict, "tags": list, "count": int}) is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_structure_should_raise_when_key_absent(make_response):
    response = make_response(SIMPLE)
    with pytest.raises(AssertionError, match="Key 'missing' missing"):
        response.assert_json_structure({"missing": str})


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_structure_should_raise_when_type_mismatches(make_response):
    response = make_response(SIMPLE)
    with pytest.raises(AssertionError, match="expected type str"):
        response.assert_json_structure({"ok": str})


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_structure_should_raise_when_payload_is_not_dict(make_response):
    response = make_response(ARRAY_BODY)
    with pytest.raises(AssertionError, match="Expected JSON dict"):
        response.assert_json_structure({"key": str})


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_structure_should_only_check_key_presence_when_type_is_none(make_response):
    response = make_response(SIMPLE)
    assert response.assert_json_structure({"ok": None}) is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_missing_path_should_pass_when_path_absent(make_response):
    response = make_response(SIMPLE)
    assert response.assert_json_missing_path("missing.path") is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_missing_path_should_raise_when_path_exists(make_response):
    response = make_response(SIMPLE)
    with pytest.raises(AssertionError, match="should not exist"):
        response.assert_json_missing_path("ok")


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_missing_path_should_pass_for_nested_absent_path(make_response):
    response = make_response(NESTED)
    assert response.assert_json_missing_path("user.nonexistent") is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_missing_path_should_pass_when_array_index_out_of_bounds(make_response):
    response = make_response(NESTED)
    assert response.assert_json_missing_path("tags.99") is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_missing_path_should_pass_when_segment_not_traversable(make_response):
    response = make_response(NESTED)
    assert response.assert_json_missing_path("count.invalid") is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_missing_path_should_pass_for_absent_path_through_array(make_response):
    response = make_response(LIST_BODY)
    assert response.assert_json_missing_path("items.0.nonexistent") is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_is_list_should_pass_when_payload_is_list(make_response):
    response = make_response(ARRAY_BODY)
    assert response.assert_json_is_list() is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_is_list_should_raise_when_payload_is_dict(make_response):
    response = make_response(SIMPLE)
    with pytest.raises(AssertionError, match="Expected JSON list"):
        response.assert_json_is_list()


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_is_dict_should_pass_when_payload_is_dict(make_response):
    response = make_response(SIMPLE)
    assert response.assert_json_is_dict() is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_is_dict_should_raise_when_payload_is_list(make_response):
    response = make_response(ARRAY_BODY)
    with pytest.raises(AssertionError, match="Expected JSON dict"):
        response.assert_json_is_dict()


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_should_return_response_when_path_and_callback_provided(make_response):
    response = make_response(NESTED)
    assert response.assert_json("user", lambda u: u.where("name", "John")) is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_should_return_scoped_assertable_when_only_path_provided(make_response):
    response = make_response(NESTED)
    scoped = response.assert_json("user")
    assert isinstance(scoped, AssertableJson)
    scoped.where("name", "John")


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_should_cache_parsed_payload_across_calls(make_response):
    response = make_response(SIMPLE)
    assert response.assert_json() is response.assert_json()


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_should_not_mutate_cache_when_scoping(make_response):
    response = make_response(NESTED)
    root_before = response.assert_json()
    response.assert_json("user", lambda u: u.where("name", "John"))
    assert response.assert_json() is root_before


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_schema_should_pass_with_inline_dict(make_response):
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]}
    assert make_response(SIMPLE).assert_json_schema(schema) is not None


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_schema_should_pass_with_file_path(make_response):
    make_response(SIMPLE).assert_json_schema(SCHEMAS_DIR / "sample_ok.json")


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_schema_should_raise_when_response_mismatches(make_response):
    wrong_schema = {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}
    with pytest.raises(AssertionError, match="schema validation failed"):
        make_response(SIMPLE).assert_json_schema(wrong_schema)


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_schema_should_return_self_for_chaining(make_response):
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
    response = make_response(SIMPLE)
    assert response.assert_json_schema(schema) is response


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_schema_should_chain_with_other_assertions(make_response):
    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
    make_response(SIMPLE).assert_ok().assert_json_schema(schema).assert_json_path("ok", True)


@pytest.mark.parametrize("make_response", JSON_RESPONSE_FACTORIES)
def test_assert_json_schema_should_pass_with_nested_response(make_response):
    make_response(NESTED).assert_json_schema(SCHEMAS_DIR / "sample_nested.json")
