from __future__ import annotations

import json
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pyssertive.formats.json import AssertableJson

SCHEMAS_DIR = Path(__file__).resolve().parents[1] / "schemas"

SAMPLE = {
    "user": {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "profile": {"age": 30, "city": "NYC"},
    },
    "tags": ["python", "django", "testing"],
    "count": 42,
    "active": True,
    "deleted_at": None,
    "error_count": 0,
}


@pytest.fixture
def doc() -> AssertableJson:
    return AssertableJson(SAMPLE)


def test_has_should_pass_when_key_present(doc: AssertableJson):
    doc.has("user")


def test_has_should_pass_for_nested_path(doc: AssertableJson):
    doc.has("user.profile.city")


def test_has_should_pass_when_count_matches(doc: AssertableJson):
    doc.has("tags", 3)


def test_has_should_raise_when_key_absent(doc: AssertableJson):
    with pytest.raises(AssertionError, match="to exist"):
        doc.has("nonexistent")


def test_has_should_raise_when_count_mismatches(doc: AssertableJson):
    with pytest.raises(AssertionError, match="Expected 5 items"):
        doc.has("tags", 5)


def test_has_should_raise_when_value_is_not_countable(doc: AssertableJson):
    with pytest.raises(AssertionError, match="countable"):
        doc.has("count", 1)


def test_missing_should_pass_when_key_absent(doc: AssertableJson):
    doc.missing("nonexistent")


def test_missing_should_pass_for_nested_absent_path(doc: AssertableJson):
    doc.missing("user.nonexistent")


def test_missing_should_raise_when_key_present(doc: AssertableJson):
    with pytest.raises(AssertionError, match="should not exist"):
        doc.missing("user")


def test_where_should_pass_when_value_matches(doc: AssertableJson):
    doc.where("user.name", "Alice")


def test_where_should_raise_when_value_mismatches(doc: AssertableJson):
    with pytest.raises(AssertionError, match="Expected 'Bob'"):
        doc.where("user.name", "Bob")


def test_where_should_evaluate_callable_predicate(doc: AssertableJson):
    doc.where("user.profile.age", lambda v: v >= 18)


def test_where_should_raise_when_predicate_returns_false(doc: AssertableJson):
    with pytest.raises(AssertionError, match="did not satisfy predicate"):
        doc.where("user.profile.age", lambda v: v > 100)


def test_where_not_should_pass_when_value_differs(doc: AssertableJson):
    doc.where_not("user.name", "Bob")


def test_where_not_should_pass_when_value_is_not_none(doc: AssertableJson):
    doc.where_not("user.name", None)


def test_where_not_should_raise_when_value_equals_unexpected(doc: AssertableJson):
    with pytest.raises(AssertionError, match="to not be"):
        doc.where_not("user.name", "Alice")


def test_where_truthy_should_pass_when_value_is_truthy(doc: AssertableJson):
    doc.where_truthy("active")


def test_where_truthy_should_raise_when_value_is_none(doc: AssertableJson):
    with pytest.raises(AssertionError, match="Expected truthy"):
        doc.where_truthy("deleted_at")


def test_where_truthy_should_raise_when_value_is_zero(doc: AssertableJson):
    with pytest.raises(AssertionError, match="Expected truthy"):
        doc.where_truthy("error_count")


def test_where_falsy_should_pass_when_value_is_none(doc: AssertableJson):
    doc.where_falsy("deleted_at")


def test_where_falsy_should_pass_when_value_is_zero(doc: AssertableJson):
    doc.where_falsy("error_count")


def test_where_falsy_should_raise_when_value_is_truthy(doc: AssertableJson):
    with pytest.raises(AssertionError, match="Expected falsy"):
        doc.where_falsy("active")


def test_where_not_should_return_self_for_method_chaining(doc: AssertableJson):
    assert doc.where_not("user.name", "Bob") is doc


def test_where_truthy_should_return_self_for_method_chaining(doc: AssertableJson):
    assert doc.where_truthy("active") is doc


def test_where_falsy_should_return_self_for_method_chaining(doc: AssertableJson):
    assert doc.where_falsy("deleted_at") is doc


def test_where_type_should_pass_when_value_matches_type(doc: AssertableJson):
    doc.where_type("user.id", int)


def test_where_type_should_pass_when_value_matches_any_in_tuple(doc: AssertableJson):
    doc.where_type("user.name", (str, bytes))


def test_where_type_should_raise_when_type_mismatches(doc: AssertableJson):
    with pytest.raises(AssertionError, match="Expected type int"):
        doc.where_type("user.name", int)


def test_count_should_pass_when_item_count_matches_at_scope():
    AssertableJson(SAMPLE["tags"]).count(3)


def test_count_should_raise_when_item_count_mismatches():
    with pytest.raises(AssertionError, match="Expected 10 items"):
        AssertableJson(SAMPLE["tags"]).count(10)


def test_count_should_raise_when_scope_is_not_countable():
    with pytest.raises(AssertionError, match="countable"):
        AssertableJson(42).count(1)


def test_fragment_should_pass_when_fragment_is_subset_of_document(doc: AssertableJson):
    doc.fragment({"count": 42})


def test_fragment_should_raise_when_fragment_is_not_subset(doc: AssertableJson):
    with pytest.raises(AssertionError, match="not found"):
        doc.fragment({"missing": "value"})


def test_missing_fragment_should_pass_when_fragment_is_absent(doc: AssertableJson):
    doc.missing_fragment({"missing": "value"})


def test_missing_fragment_should_raise_when_fragment_is_present(doc: AssertableJson):
    with pytest.raises(AssertionError, match="Unexpected fragment"):
        doc.missing_fragment({"count": 42})


def test_exact_should_pass_when_value_matches_full_document(doc: AssertableJson):
    doc.exact(SAMPLE)


def test_exact_should_raise_when_value_differs_from_document(doc: AssertableJson):
    with pytest.raises(AssertionError, match="Expected exact JSON"):
        doc.exact({"different": True})


def test_is_dict_should_pass_when_scope_is_dict(doc: AssertableJson):
    doc.is_dict()


def test_is_dict_should_raise_when_scope_is_not_dict():
    with pytest.raises(AssertionError, match="Expected JSON dict"):
        AssertableJson([1, 2]).is_dict()


def test_is_list_should_pass_when_scope_is_list():
    AssertableJson([1, 2]).is_list()


def test_is_list_should_raise_when_scope_is_not_list(doc: AssertableJson):
    with pytest.raises(AssertionError, match="Expected JSON list"):
        doc.is_list()


def test_structure_should_pass_when_keys_and_types_match(doc: AssertableJson):
    doc.structure({"user": dict, "tags": list, "count": int})


def test_structure_should_only_check_key_presence_when_type_is_none(doc: AssertableJson):
    doc.structure({"user": None})


def test_structure_should_raise_when_key_absent(doc: AssertableJson):
    with pytest.raises(AssertionError, match="Key 'missing' missing"):
        doc.structure({"missing": str})


def test_structure_should_raise_when_type_mismatches(doc: AssertableJson):
    with pytest.raises(AssertionError, match="expected type str"):
        doc.structure({"count": str})


def test_structure_should_raise_when_scope_is_not_dict():
    with pytest.raises(AssertionError, match="Expected JSON dict"):
        AssertableJson([1]).structure({"key": int})


def test_json_should_return_self_when_callback_provided(doc: AssertableJson):
    result = doc.json("user", lambda u: u.where("name", "Alice"))
    assert result is doc


def test_json_should_return_new_scoped_assertable_when_no_callback(doc: AssertableJson):
    scoped = doc.json("user")
    assert isinstance(scoped, AssertableJson)
    assert scoped is not doc
    scoped.where("name", "Alice")


def test_json_should_scope_assertions_to_sub_path(doc: AssertableJson):
    doc.json("user", lambda u: u.where("name", "Alice").missing("tags"))


def test_json_should_support_nested_scoping(doc: AssertableJson):
    doc.json("user", lambda u: u.json("profile", lambda p: p.where("age", 30).where("city", "NYC")))


def test_json_should_include_parent_path_in_nested_error_message(doc: AssertableJson):
    with pytest.raises(AssertionError, match=re.escape("user.profile.nonexistent")):
        doc.json("user", lambda u: u.json("profile", lambda p: p.has("nonexistent")))


def test_json_should_raise_when_path_not_found(doc: AssertableJson):
    with pytest.raises(AssertionError, match="not found"):
        doc.json("nonexistent")


def test_json_should_support_numeric_array_indexes_in_path(doc: AssertableJson):
    doc.json("tags.0", lambda t: t.exact("python"))


def test_json_should_raise_when_array_index_out_of_range(doc: AssertableJson):
    with pytest.raises(AssertionError, match="out of range"):
        doc.json("tags.99")


def test_path_resolver_should_raise_when_path_not_traversable(doc: AssertableJson):
    with pytest.raises(AssertionError, match="not traversable"):
        doc.where("count.invalid", "x")


def test_has_should_return_self_for_method_chaining(doc: AssertableJson):
    assert doc.has("user") is doc


def test_missing_should_return_self_for_method_chaining(doc: AssertableJson):
    assert doc.missing("nonexistent") is doc


def test_where_should_return_self_for_method_chaining(doc: AssertableJson):
    assert doc.where("count", 42) is doc


def test_where_type_should_return_self_for_method_chaining(doc: AssertableJson):
    assert doc.where_type("count", int) is doc


def test_is_dict_should_return_self_for_method_chaining(doc: AssertableJson):
    assert doc.is_dict() is doc


def test_is_list_should_return_self_for_method_chaining():
    a = AssertableJson([1])
    assert a.is_list() is a


def test_fragment_should_return_self_for_method_chaining(doc: AssertableJson):
    assert doc.fragment({"count": 42}) is doc


def test_exact_should_return_self_for_method_chaining(doc: AssertableJson):
    assert doc.exact(SAMPLE) is doc


def test_structure_should_return_self_for_method_chaining(doc: AssertableJson):
    assert doc.structure({"user": None}) is doc


def test_missing_fragment_should_return_self_for_method_chaining(doc: AssertableJson):
    assert doc.missing_fragment({"x": 1}) is doc


def test_constructor_should_parse_string_payload_as_json():
    AssertableJson('{"ok": true}').where("ok", True)


def test_constructor_should_parse_bytes_payload_as_json():
    AssertableJson(b'{"ok": true}').where("ok", True)


VALID_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "user": {"type": "object"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "count": {"type": "integer"},
    },
    "required": ["user", "tags", "count"],
}


def test_matches_schema_should_pass_when_data_conforms(doc: AssertableJson):
    doc.matches_schema(VALID_SCHEMA)


def test_matches_schema_should_raise_when_required_field_missing():
    data = {"tags": ["python"]}
    with pytest.raises(AssertionError, match="schema validation failed"):
        AssertableJson(data).matches_schema(VALID_SCHEMA)


def test_matches_schema_should_raise_when_type_mismatches():
    data = {**SAMPLE, "count": "not_an_int"}
    with pytest.raises(AssertionError, match="schema validation failed"):
        AssertableJson(data).matches_schema(VALID_SCHEMA)


def test_matches_schema_should_report_failing_path():
    data = {**SAMPLE, "tags": "not_a_list"}
    with pytest.raises(AssertionError, match="'tags'"):
        AssertableJson(data).matches_schema(VALID_SCHEMA)


def test_matches_schema_should_return_self_for_method_chaining(doc: AssertableJson):
    assert doc.matches_schema(VALID_SCHEMA) is doc


def test_matches_schema_should_pass_with_str_file_path(doc: AssertableJson):
    doc.matches_schema(str(SCHEMAS_DIR / "sample_nested.json"))


def test_matches_schema_should_pass_with_path_object(doc: AssertableJson):
    doc.matches_schema(SCHEMAS_DIR / "sample_nested.json")


def test_matches_schema_should_raise_when_file_not_found(doc: AssertableJson):
    with pytest.raises(FileNotFoundError, match="Schema file not found"):
        doc.matches_schema("nonexistent/schema.json")


def test_matches_schema_should_raise_when_file_schema_mismatches():
    data = {"ok": "not_a_bool"}
    with pytest.raises(AssertionError, match="schema validation failed"):
        AssertableJson(data).matches_schema(SCHEMAS_DIR / "sample_ok.json")


def test_matches_schema_should_pass_with_url_schema(doc: AssertableJson):
    remote_schema = json.dumps(VALID_SCHEMA).encode()
    mock_response = MagicMock()
    mock_response.read.return_value = remote_schema
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    with patch("pyssertive.formats.json.urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        doc.matches_schema("https://api.example.com/schemas/sample.json")
    mock_urlopen.assert_called_once_with("https://api.example.com/schemas/sample.json")


def test_matches_schema_should_raise_with_url_schema_when_data_invalid():
    strict_schema = json.dumps(
        {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}
    ).encode()
    mock_response = MagicMock()
    mock_response.read.return_value = strict_schema
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    with (
        patch("pyssertive.formats.json.urllib.request.urlopen", return_value=mock_response),
        pytest.raises(AssertionError, match="schema validation failed"),
    ):
        AssertableJson({"ok": True}).matches_schema("https://api.example.com/schemas/strict.json")


def test_matches_schema_should_include_scope_in_error_message():
    user_schema = {
        "type": "object",
        "properties": {"id": {"type": "string"}},
        "required": ["id"],
    }
    scoped = AssertableJson(SAMPLE["user"], _path="user")
    with pytest.raises(AssertionError, match="at scope 'user'"):
        scoped.matches_schema(user_schema)
