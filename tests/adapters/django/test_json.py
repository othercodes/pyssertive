import pytest

from pyssertive.adapters.django import FluentHttpAssertClient


@pytest.mark.django_db
def test_assert_json_should_return_assertable_json_when_no_arguments(fluent_admin_client: FluentHttpAssertClient):
    from pyssertive.http.json import AssertableJson

    response = fluent_admin_client.get("/json/")
    result = response.assert_json()
    assert isinstance(result, AssertableJson)


@pytest.mark.django_db
def test_assert_json_should_raise_when_payload_is_invalid(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/invalid-json/")
    with pytest.raises(AssertionError, match="not valid JSON"):
        response.assert_json()


@pytest.mark.django_db
def test_assert_json_path_should_pass_when_value_matches_at_path(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_path("ok", True)
    assert result is response


@pytest.mark.django_db
def test_assert_json_path_should_resolve_nested_paths(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-list/")
    result = response.assert_json_path("items.0.id", 1)
    assert result is response


@pytest.mark.django_db
def test_assert_json_path_should_raise_when_value_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected"):
        response.assert_json_path("ok", False)


@pytest.mark.django_db
def test_assert_json_path_should_raise_when_path_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="not found"):
        response.assert_json_path("missing.path", True)


@pytest.mark.django_db
def test_assert_json_fragment_should_pass_when_fragment_is_subset(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_fragment({"ok": True})
    assert result is response


@pytest.mark.django_db
def test_assert_json_fragment_should_raise_when_fragment_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="not found"):
        response.assert_json_fragment({"missing": "value"})


@pytest.mark.django_db
def test_assert_json_missing_fragment_should_pass_when_fragment_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_missing_fragment({"missing": "value"})
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_fragment_should_raise_when_fragment_present(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Unexpected fragment"):
        response.assert_json_missing_fragment({"ok": True})


@pytest.mark.django_db
def test_assert_json_count_should_pass_when_count_matches_at_path(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-list/")
    result = response.assert_json_count(3, path="items")
    assert result is response


@pytest.mark.django_db
def test_assert_json_count_should_apply_at_root_when_no_path_given(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-list/")
    with pytest.raises(AssertionError, match="Expected 3 items"):
        response.assert_json_count(3)


@pytest.mark.django_db
def test_assert_json_count_should_raise_when_count_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-list/")
    with pytest.raises(AssertionError, match="Expected 5 items"):
        response.assert_json_count(5, path="items")


@pytest.mark.django_db
def test_assert_json_count_should_raise_when_value_is_not_countable(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="countable"):
        response.assert_json_count(1, path="ok")


@pytest.mark.django_db
def test_assert_exact_json_should_pass_when_payload_matches_full_value(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_exact_json({"ok": True})
    assert result is response


@pytest.mark.django_db
def test_assert_exact_json_should_raise_when_payload_differs(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected exact JSON"):
        response.assert_exact_json({"ok": True, "extra": "field"})


@pytest.mark.django_db
def test_assert_json_structure_should_pass_when_keys_and_types_match(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-nested/")
    result = response.assert_json_structure(
        {
            "user": dict,
            "tags": list,
            "count": int,
        }
    )
    assert result is response


@pytest.mark.django_db
def test_assert_json_structure_should_raise_when_key_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Key 'missing' missing"):
        response.assert_json_structure({"missing": str})


@pytest.mark.django_db
def test_assert_json_structure_should_raise_when_type_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="expected type str"):
        response.assert_json_structure({"ok": str})


@pytest.mark.django_db
def test_assert_json_structure_should_raise_when_payload_is_not_dict(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-array/")
    with pytest.raises(AssertionError, match="Expected JSON dict"):
        response.assert_json_structure({"key": str})


@pytest.mark.django_db
def test_assert_json_structure_should_only_check_key_presence_when_type_is_none(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_structure({"ok": None})
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_should_pass_when_path_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_missing_path("missing.path")
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_should_raise_when_path_exists(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="should not exist"):
        response.assert_json_missing_path("ok")


@pytest.mark.django_db
def test_assert_json_missing_path_should_pass_for_nested_absent_path(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-nested/")
    result = response.assert_json_missing_path("user.nonexistent")
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_should_pass_when_array_index_out_of_bounds(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json-nested/")
    result = response.assert_json_missing_path("tags.99")
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_should_pass_when_segment_not_traversable(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json-nested/")
    result = response.assert_json_missing_path("count.invalid")
    assert result is response


@pytest.mark.django_db
def test_assert_json_missing_path_should_pass_for_absent_path_through_array(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json-list/")
    result = response.assert_json_missing_path("items.0.nonexistent")
    assert result is response


@pytest.mark.django_db
def test_assert_json_is_list_should_pass_when_payload_is_list(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-array/")
    result = response.assert_json_is_list()
    assert result is response


@pytest.mark.django_db
def test_assert_json_is_list_should_raise_when_payload_is_dict(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Expected JSON list"):
        response.assert_json_is_list()


@pytest.mark.django_db
def test_assert_json_is_dict_should_pass_when_payload_is_dict(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    result = response.assert_json_is_dict()
    assert result is response


@pytest.mark.django_db
def test_assert_json_is_dict_should_raise_when_payload_is_list(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-array/")
    with pytest.raises(AssertionError, match="Expected JSON dict"):
        response.assert_json_is_dict()


@pytest.mark.django_db
def test_assert_json_is_array_should_warn_as_deprecated_alias(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-array/")
    with pytest.warns(DeprecationWarning, match="assert_json_is_array"):
        result = response.assert_json_is_array()
    assert result is response


@pytest.mark.django_db
def test_assert_json_is_object_should_warn_as_deprecated_alias(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.warns(DeprecationWarning, match="assert_json_is_object"):
        result = response.assert_json_is_object()
    assert result is response


@pytest.mark.django_db
def test_assert_json_should_return_response_when_path_and_callback_provided(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json-nested/")
    result = response.assert_json("user", lambda u: u.where("name", "John"))
    assert result is response


@pytest.mark.django_db
def test_assert_json_should_return_scoped_assertable_when_only_path_provided(
    fluent_admin_client: FluentHttpAssertClient,
):
    from pyssertive.http.json import AssertableJson

    response = fluent_admin_client.get("/json-nested/")
    scoped = response.assert_json("user")
    assert isinstance(scoped, AssertableJson)
    scoped.where("name", "John")


@pytest.mark.django_db
def test_assert_json_should_cache_parsed_payload_across_calls(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    first = response.assert_json()
    second = response.assert_json()
    assert first is second


@pytest.mark.django_db
def test_assert_json_should_not_mutate_cache_when_scoping(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json-nested/")
    root_before = response.assert_json()
    response.assert_json("user", lambda u: u.where("name", "John"))
    root_after = response.assert_json()
    assert root_before is root_after
