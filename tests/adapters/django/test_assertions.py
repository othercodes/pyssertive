import pytest
from django.http import HttpResponse

from pyssertive.adapters.django import FluentHttpAssertClient, FluentResponse


@pytest.mark.django_db
def test_assert_template_used_should_pass_when_template_was_rendered(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    result = response.assert_template_used("test_template.html")
    assert result is response


@pytest.mark.django_db
def test_assert_template_used_should_raise_when_template_was_not_rendered(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    with pytest.raises(AssertionError):
        response.assert_template_used("wrong_template.html")


@pytest.mark.django_db
def test_assert_template_not_used_should_pass_when_template_was_not_rendered(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/template/")
    result = response.assert_template_not_used("wrong_template.html")
    assert result is response


@pytest.mark.django_db
def test_assert_template_not_used_should_raise_when_template_was_rendered(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    with pytest.raises(AssertionError):
        response.assert_template_not_used("test_template.html")


@pytest.mark.django_db
def test_assert_context_has_should_pass_when_key_present_in_context(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    result = response.assert_context_has("title")
    assert result is response


@pytest.mark.django_db
def test_assert_context_has_should_raise_when_key_absent_from_context(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    with pytest.raises(AssertionError, match="Expected context to contain"):
        response.assert_context_has("missing_key")


@pytest.mark.django_db
def test_assert_context_has_should_raise_when_response_has_no_context(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Response has no context"):
        response.assert_context_has("key")


@pytest.mark.django_db
def test_assert_context_equals_should_pass_when_value_matches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    result = response.assert_context_equals("title", "Test Title")
    assert result is response


@pytest.mark.django_db
def test_assert_context_equals_should_raise_when_value_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    with pytest.raises(AssertionError, match="Expected context"):
        response.assert_context_equals("title", "Wrong Title")


@pytest.mark.django_db
def test_assert_context_equals_should_raise_when_response_has_no_context(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="Response has no context"):
        response.assert_context_equals("key", "value")


@pytest.mark.django_db
def test_assert_form_error_should_pass_when_form_has_expected_field_error(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/form-error/")
    result = response.assert_form_error("form", "name", "This field is required.")
    assert result is response


@pytest.mark.django_db
def test_assert_form_error_should_raise_when_response_is_not_a_template_response(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="must be a TemplateResponse"):
        response.assert_form_error("form", "field", "error")


@pytest.mark.django_db
def test_assert_form_error_should_raise_when_form_name_absent_from_context(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    with pytest.raises(AssertionError, match="not found in response context"):
        response.assert_form_error("form", "field", "error")


@pytest.mark.django_db
def test_assert_form_error_should_raise_when_context_value_is_not_a_form(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/template/")
    with pytest.raises(AssertionError, match="is not a Form instance"):
        response.assert_form_error("title", "field", "error")


@pytest.mark.django_db
def test_assert_formset_error_should_pass_when_formset_has_expected_field_error(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/formset-error/")
    result = response.assert_formset_error("formset", 0, "name", "This field is required.")
    assert result is response


@pytest.mark.django_db
def test_assert_formset_error_should_raise_when_response_is_not_a_template_response(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/json/")
    with pytest.raises(AssertionError, match="must be a TemplateResponse"):
        response.assert_formset_error("formset", 0, "field", "error")


@pytest.mark.django_db
def test_assert_formset_error_should_raise_when_formset_name_absent_from_context(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/template/")
    with pytest.raises(AssertionError, match="not found in response context"):
        response.assert_formset_error("formset", 0, "field", "error")


@pytest.mark.django_db
def test_assert_formset_error_should_raise_when_context_value_is_not_a_formset(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/template/")
    with pytest.raises(AssertionError, match="is not a FormSet instance"):
        response.assert_formset_error("title", 0, "field", "error")


@pytest.mark.django_db
def test_assert_session_has_should_pass_when_key_present_in_session(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/session-set/")
    result = response.assert_session_has("user_id")
    assert result is response


@pytest.mark.django_db
def test_assert_session_has_should_pass_when_key_and_value_match(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/session-set/")
    result = response.assert_session_has("user_id", 123)
    assert result is response


@pytest.mark.django_db
def test_assert_session_has_should_raise_when_key_absent_from_session(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/session-set/")
    with pytest.raises(AssertionError, match="Session key 'missing' not found"):
        response.assert_session_has("missing")


@pytest.mark.django_db
def test_assert_session_has_should_raise_when_value_mismatches(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/session-set/")
    with pytest.raises(AssertionError, match="expected '999'"):
        response.assert_session_has("user_id", 999)


@pytest.mark.django_db
def test_assert_session_missing_should_pass_when_key_absent_from_session(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/session-set/")
    result = response.assert_session_missing("nonexistent")
    assert result is response


@pytest.mark.django_db
def test_assert_session_missing_should_raise_when_key_present_in_session(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/session-set/")
    with pytest.raises(AssertionError, match="should not exist"):
        response.assert_session_missing("user_id")


@pytest.mark.django_db
def test_assert_session_has_all_should_pass_when_every_key_present_in_session(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/session-set/")
    result = response.assert_session_has_all(["user_id", "username"])
    assert result is response


@pytest.mark.django_db
def test_assert_session_has_all_should_raise_when_any_key_absent_from_session(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/session-set/")
    with pytest.raises(AssertionError, match="Session missing keys"):
        response.assert_session_has_all(["user_id", "nonexistent"])


@pytest.mark.django_db
def test_assert_session_should_raise_when_response_has_no_request_context(fluent_admin_client: FluentHttpAssertClient):
    response = FluentResponse(HttpResponse("test"))
    with pytest.raises(AssertionError, match="no request context"):
        response.assert_session_has("key")
