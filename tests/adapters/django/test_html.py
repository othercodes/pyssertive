import pytest

from pyssertive.adapters.django import FluentHttpAssertClient


@pytest.mark.django_db
def test_assert_see_html_should_pass_when_text_present_in_markup(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    result = response.assert_see_html("Hello World")
    assert result is response


@pytest.mark.django_db
def test_assert_see_html_should_match_html_markup_fragments(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    result = response.assert_see_html("<strong>bold text</strong>")
    assert result is response


@pytest.mark.django_db
def test_assert_see_html_should_raise_when_text_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Expected to see HTML markup"):
        response.assert_see_html("Missing Text")


@pytest.mark.django_db
def test_assert_dont_see_html_should_pass_when_text_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    result = response.assert_dont_see_html("Missing Text")
    assert result is response


@pytest.mark.django_db
def test_assert_dont_see_html_should_raise_when_text_present(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Did not expect HTML markup"):
        response.assert_dont_see_html("Hello World")


@pytest.mark.django_db
def test_assert_see_text_should_pass_when_text_visible_in_rendered_output(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    result = response.assert_see_text("bold text")
    assert result is response


@pytest.mark.django_db
def test_assert_see_text_should_not_match_html_tags(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Expected to see rendered text"):
        response.assert_see_text("<strong>")


@pytest.mark.django_db
def test_assert_see_text_should_raise_when_text_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Expected to see rendered text"):
        response.assert_see_text("Missing")


@pytest.mark.django_db
def test_assert_dont_see_text_should_pass_when_text_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    result = response.assert_dont_see_text("Missing")
    assert result is response


@pytest.mark.django_db
def test_assert_dont_see_text_should_raise_when_text_present(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Did not expect rendered text"):
        response.assert_dont_see_text("bold text")


@pytest.mark.django_db
def test_assert_see_html_in_order_should_pass_when_fragments_appear_in_sequence(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    result = response.assert_see_html_in_order(["Hello", "<strong>bold"])
    assert result is response


@pytest.mark.django_db
def test_assert_see_html_in_order_should_raise_when_fragment_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="HTML markup 'Missing'"):
        response.assert_see_html_in_order(["Hello", "Missing"])


@pytest.mark.django_db
def test_assert_see_html_in_order_should_raise_when_order_is_wrong(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="after 'test page'"):
        response.assert_see_html_in_order(["test page", "Hello"])


@pytest.mark.django_db
def test_assert_see_text_in_order_should_pass_when_texts_appear_in_sequence(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    result = response.assert_see_text_in_order(["Hello", "bold text"])
    assert result is response


@pytest.mark.django_db
def test_assert_see_text_in_order_should_raise_when_text_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="Rendered text 'Missing'"):
        response.assert_see_text_in_order(["Hello", "Missing"])


@pytest.mark.django_db
def test_assert_see_text_in_order_should_raise_when_order_is_wrong(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError, match="after 'bold text'"):
        response.assert_see_text_in_order(["bold text", "Hello"])


@pytest.mark.django_db
def test_assert_html_contains_should_pass_when_fragment_present_in_document(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    result = response.assert_html_contains("<h1>Hello World</h1>")
    assert result is response


@pytest.mark.django_db
def test_assert_html_contains_should_raise_when_fragment_absent(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.raises(AssertionError):
        response.assert_html_contains("<h1>Missing</h1>")


@pytest.mark.django_db
def test_assert_see_should_warn_as_deprecated_alias_and_still_assert(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html/")
    with pytest.warns(DeprecationWarning, match="assert_see\\(\\) is deprecated"):
        result = response.assert_see("Hello World")
    assert result is response


@pytest.mark.django_db
def test_assert_see_should_warn_as_deprecated_alias_and_raise_when_absent(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    with pytest.warns(DeprecationWarning), pytest.raises(AssertionError, match="Expected to see HTML markup"):
        response.assert_see("Missing Text")


@pytest.mark.django_db
def test_assert_dont_see_should_warn_as_deprecated_alias_and_still_assert(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    with pytest.warns(DeprecationWarning, match="assert_dont_see\\(\\) is deprecated"):
        result = response.assert_dont_see("Missing Text")
    assert result is response


@pytest.mark.django_db
def test_assert_dont_see_should_warn_as_deprecated_alias_and_raise_when_present(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    with pytest.warns(DeprecationWarning), pytest.raises(AssertionError, match="Did not expect HTML markup"):
        response.assert_dont_see("Hello World")


@pytest.mark.django_db
def test_assert_see_in_order_should_warn_as_deprecated_alias_and_still_assert(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    with pytest.warns(DeprecationWarning, match="assert_see_in_order\\(\\) is deprecated"):
        result = response.assert_see_in_order(["Hello", "test page"])
    assert result is response


@pytest.mark.django_db
def test_assert_see_in_order_should_warn_as_deprecated_alias_and_raise_when_fragment_absent(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html/")
    with pytest.warns(DeprecationWarning), pytest.raises(AssertionError, match="not found"):
        response.assert_see_in_order(["Hello", "Missing"])


@pytest.mark.django_db
def test_assert_html_should_return_response_when_selector_and_callback_provided(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html-sections/")
    result = response.assert_html(
        "table#active-users",
        lambda users: users.count("tbody tr", 3).see_text("Alice"),
    )
    assert result is response


@pytest.mark.django_db
def test_assert_html_should_return_document_assertable_when_no_arguments(fluent_admin_client: FluentHttpAssertClient):
    from pyssertive.http.html import AssertableHtml

    response = fluent_admin_client.get("/html-sections/")
    doc = response.assert_html()
    assert isinstance(doc, AssertableHtml)


@pytest.mark.django_db
def test_assert_html_should_return_scoped_assertable_when_only_selector_provided(
    fluent_admin_client: FluentHttpAssertClient,
):
    from pyssertive.http.html import AssertableHtml

    response = fluent_admin_client.get("/html-sections/")
    table = response.assert_html("table#active-users")
    assert isinstance(table, AssertableHtml)
    table.count("tbody tr", 3)


@pytest.mark.django_db
def test_assert_html_should_raise_when_selector_does_not_match(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html-sections/")
    with pytest.raises(AssertionError, match="Selector 'table#nonexistent' not found"):
        response.assert_html("table#nonexistent", lambda _: None)


@pytest.mark.django_db
def test_assert_html_should_isolate_assertions_to_scoped_section(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html-sections/")
    result = (
        response.assert_ok()
        .assert_html("section#billing", lambda s: s.see_text("alice@example.com"))
        .assert_html("section#audit-log", lambda s: s.dont_see_text("alice@example.com").see_text("bob@example.com"))
    )
    assert result is response


@pytest.mark.django_db
def test_assert_html_should_cache_parsed_document_across_calls(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html-sections/")
    first = response.assert_html()
    second = response.assert_html()
    assert first is second


@pytest.mark.django_db
def test_assert_html_should_not_contaminate_cache_when_alternating_root_and_scoped_calls(
    fluent_admin_client: FluentHttpAssertClient,
):
    response = fluent_admin_client.get("/html-sections/")
    result = (
        response.assert_ok()
        .assert_see_text("Dashboard")
        .assert_html("table#active-users", lambda t: t.count("tbody tr.row", 3).see_text("Alice"))
        .assert_html("section#billing", lambda s: s.see_text("alice@example.com").dont_see_text("Carol"))
        .assert_html("section#audit-log", lambda s: s.see_text("bob@example.com").dont_see_text("Alice"))
        .assert_see_text("Footer text outside the table")
    )
    assert result is response


@pytest.mark.django_db
def test_assert_html_should_not_mutate_cached_root_when_scoping(fluent_admin_client: FluentHttpAssertClient):
    response = fluent_admin_client.get("/html-sections/")
    root_before = response.assert_html()
    response.assert_html("table#active-users", lambda t: t.count("tbody tr.row", 3))
    root_after = response.assert_html()
    assert root_before is root_after
    response.assert_see_text("Dashboard").assert_see_text("Footer text outside the table")
