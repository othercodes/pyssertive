import pytest

from pyssertive.adapters.django import FluentHttpAssertClient


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
