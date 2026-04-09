from __future__ import annotations

import re

import pytest

from pyssertive.http.json import AssertableJson

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


def test_has_existing_key(doc: AssertableJson) -> None:
    doc.has("user")


def test_has_nested_path(doc: AssertableJson) -> None:
    doc.has("user.profile.city")


def test_has_with_count(doc: AssertableJson) -> None:
    doc.has("tags", 3)


def test_has_fails_for_missing(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="to exist"):
        doc.has("nonexistent")


def test_has_fails_for_wrong_count(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="Expected 5 items"):
        doc.has("tags", 5)


def test_has_fails_for_non_countable(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="countable"):
        doc.has("count", 1)


def test_missing_passes(doc: AssertableJson) -> None:
    doc.missing("nonexistent")


def test_missing_nested_passes(doc: AssertableJson) -> None:
    doc.missing("user.nonexistent")


def test_missing_fails_when_present(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="should not exist"):
        doc.missing("user")


def test_where_exact_value(doc: AssertableJson) -> None:
    doc.where("user.name", "Alice")


def test_where_fails_for_wrong_value(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="Expected 'Bob'"):
        doc.where("user.name", "Bob")


def test_where_with_predicate(doc: AssertableJson) -> None:
    doc.where("user.profile.age", lambda v: v >= 18)


def test_where_predicate_fails(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="did not satisfy predicate"):
        doc.where("user.profile.age", lambda v: v > 100)


def test_where_not_passes(doc: AssertableJson) -> None:
    doc.where_not("user.name", "Bob")


def test_where_not_none(doc: AssertableJson) -> None:
    doc.where_not("user.name", None)


def test_where_not_fails_when_equal(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="to not be"):
        doc.where_not("user.name", "Alice")


def test_where_truthy_passes(doc: AssertableJson) -> None:
    doc.where_truthy("active")


def test_where_truthy_fails_for_none(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="Expected truthy"):
        doc.where_truthy("deleted_at")


def test_where_truthy_fails_for_zero(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="Expected truthy"):
        doc.where_truthy("error_count")


def test_where_falsy_passes_for_none(doc: AssertableJson) -> None:
    doc.where_falsy("deleted_at")


def test_where_falsy_passes_for_zero(doc: AssertableJson) -> None:
    doc.where_falsy("error_count")


def test_where_falsy_fails_for_truthy(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="Expected falsy"):
        doc.where_falsy("active")


def test_where_not_returns_self_for_chaining(doc: AssertableJson) -> None:
    assert doc.where_not("user.name", "Bob") is doc


def test_where_truthy_returns_self_for_chaining(doc: AssertableJson) -> None:
    assert doc.where_truthy("active") is doc


def test_where_falsy_returns_self_for_chaining(doc: AssertableJson) -> None:
    assert doc.where_falsy("deleted_at") is doc


def test_where_type_passes(doc: AssertableJson) -> None:
    doc.where_type("user.id", int)


def test_where_type_tuple(doc: AssertableJson) -> None:
    doc.where_type("user.name", (str, bytes))


def test_where_type_fails(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="Expected type int"):
        doc.where_type("user.name", int)


def test_count_at_scope(doc: AssertableJson) -> None:
    AssertableJson(SAMPLE["tags"]).count(3)


def test_count_fails_for_wrong_number(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="Expected 10 items"):
        AssertableJson(SAMPLE["tags"]).count(10)


def test_count_fails_for_non_countable() -> None:
    with pytest.raises(AssertionError, match="countable"):
        AssertableJson(42).count(1)


def test_fragment_passes(doc: AssertableJson) -> None:
    doc.fragment({"count": 42})


def test_fragment_fails(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="not found"):
        doc.fragment({"missing": "value"})


def test_missing_fragment_passes(doc: AssertableJson) -> None:
    doc.missing_fragment({"missing": "value"})


def test_missing_fragment_fails(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="Unexpected fragment"):
        doc.missing_fragment({"count": 42})


def test_exact_passes(doc: AssertableJson) -> None:
    doc.exact(SAMPLE)


def test_exact_fails(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="Expected exact JSON"):
        doc.exact({"different": True})


def test_is_dict_passes(doc: AssertableJson) -> None:
    doc.is_dict()


def test_is_dict_fails() -> None:
    with pytest.raises(AssertionError, match="Expected JSON dict"):
        AssertableJson([1, 2]).is_dict()


def test_is_list_passes() -> None:
    AssertableJson([1, 2]).is_list()


def test_is_list_fails(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="Expected JSON list"):
        doc.is_list()


def test_structure_passes(doc: AssertableJson) -> None:
    doc.structure({"user": dict, "tags": list, "count": int})


def test_structure_with_none_type(doc: AssertableJson) -> None:
    doc.structure({"user": None})


def test_structure_fails_for_missing_key(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="Key 'missing' missing"):
        doc.structure({"missing": str})


def test_structure_fails_for_wrong_type(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="expected type str"):
        doc.structure({"count": str})


def test_structure_fails_for_non_dict() -> None:
    with pytest.raises(AssertionError, match="Expected JSON dict"):
        AssertableJson([1]).structure({"key": int})


def test_json_scoping_with_callback_returns_self(doc: AssertableJson) -> None:
    result = doc.json("user", lambda u: u.where("name", "Alice"))
    assert result is doc


def test_json_scoping_without_callback_returns_new_scope(doc: AssertableJson) -> None:
    scoped = doc.json("user")
    assert isinstance(scoped, AssertableJson)
    assert scoped is not doc
    scoped.where("name", "Alice")


def test_json_scoping_scopes_content_properly(doc: AssertableJson) -> None:
    doc.json("user", lambda u: u.where("name", "Alice").missing("tags"))


def test_json_scoping_nested(doc: AssertableJson) -> None:
    doc.json("user", lambda u: u.json("profile", lambda p: p.where("age", 30).where("city", "NYC")))


def test_json_scoping_child_path_includes_parent(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match=re.escape("user.profile.nonexistent")):
        doc.json("user", lambda u: u.json("profile", lambda p: p.has("nonexistent")))


def test_json_scoping_missing_path(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="not found"):
        doc.json("nonexistent")


def test_json_scoping_array_index(doc: AssertableJson) -> None:
    doc.json("tags.0", lambda t: t.exact("python"))


def test_json_scoping_array_index_out_of_bounds(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="out of range"):
        doc.json("tags.99")


def test_resolve_non_traversable(doc: AssertableJson) -> None:
    with pytest.raises(AssertionError, match="not traversable"):
        doc.where("count.invalid", "x")


def test_has_returns_self_for_chaining(doc: AssertableJson) -> None:
    assert doc.has("user") is doc


def test_missing_returns_self_for_chaining(doc: AssertableJson) -> None:
    assert doc.missing("nonexistent") is doc


def test_where_returns_self_for_chaining(doc: AssertableJson) -> None:
    assert doc.where("count", 42) is doc


def test_where_type_returns_self_for_chaining(doc: AssertableJson) -> None:
    assert doc.where_type("count", int) is doc


def test_is_dict_returns_self_for_chaining(doc: AssertableJson) -> None:
    assert doc.is_dict() is doc


def test_is_list_returns_self_for_chaining() -> None:
    a = AssertableJson([1])
    assert a.is_list() is a


def test_fragment_returns_self_for_chaining(doc: AssertableJson) -> None:
    assert doc.fragment({"count": 42}) is doc


def test_exact_returns_self_for_chaining(doc: AssertableJson) -> None:
    assert doc.exact(SAMPLE) is doc


def test_structure_returns_self_for_chaining(doc: AssertableJson) -> None:
    assert doc.structure({"user": None}) is doc


def test_missing_fragment_returns_self_for_chaining(doc: AssertableJson) -> None:
    assert doc.missing_fragment({"x": 1}) is doc
