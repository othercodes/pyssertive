from __future__ import annotations

import pytest

from pyssertive.formats.html import AssertableHtml
from tests.adapters._factories import _make_django_response, _make_httpx_response, _pair

HTML_RESPONSE_FACTORIES = _pair(
    lambda markup, status=200: _make_django_response(markup, status=status, content_type="text/html"),
    lambda markup, status=200: _make_httpx_response(markup, status=status, content_type="text/html"),
)

SIMPLE_HTML = """<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body>
<h1>Hello World</h1>
<p>This is a test page with <strong>bold text</strong>.</p>
</body>
</html>"""


SECTIONS_HTML = """<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
<h1>Dashboard</h1>
<nav class="main"><ul><li>Home</li><li>Users</li><li>Settings</li></ul></nav>
<section id="billing">
  <h2>Billing</h2>
  <p>Contact: <span class="email">alice@example.com</span></p>
</section>
<section id="audit-log">
  <h2>Audit Log</h2>
  <p>Reviewed by: <span class="email">bob@example.com</span></p>
</section>
<table id="active-users">
  <thead><tr><th>Name</th><th>Email</th></tr></thead>
  <tbody>
    <tr class="row"><td>Alice</td><td>alice@example.com</td></tr>
    <tr class="row"><td>Bob</td><td>bob@example.com</td></tr>
    <tr class="row"><td>Carol</td><td>carol@example.com</td></tr>
  </tbody>
</table>
<footer>Footer text outside the table</footer>
</body>
</html>"""


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_see_html_should_pass_when_text_present_in_markup(make_response):
    response = make_response(SIMPLE_HTML)
    assert response.assert_see_html("Hello World") is response


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_see_html_should_match_html_markup_fragments(make_response):
    response = make_response(SIMPLE_HTML)
    assert response.assert_see_html("<strong>bold text</strong>") is response


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_see_html_should_raise_when_text_absent(make_response):
    response = make_response(SIMPLE_HTML)
    with pytest.raises(AssertionError, match="Expected to see HTML markup"):
        response.assert_see_html("Missing Text")


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_dont_see_html_should_pass_when_text_absent(make_response):
    response = make_response(SIMPLE_HTML)
    assert response.assert_dont_see_html("Missing Text") is response


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_dont_see_html_should_raise_when_text_present(make_response):
    response = make_response(SIMPLE_HTML)
    with pytest.raises(AssertionError, match="Did not expect HTML markup"):
        response.assert_dont_see_html("Hello World")


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_see_text_should_pass_when_text_visible_in_rendered_output(make_response):
    response = make_response(SIMPLE_HTML)
    assert response.assert_see_text("bold text") is response


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_see_text_should_not_match_html_tags(make_response):
    response = make_response(SIMPLE_HTML)
    with pytest.raises(AssertionError, match="Expected to see rendered text"):
        response.assert_see_text("<strong>")


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_see_text_should_raise_when_text_absent(make_response):
    response = make_response(SIMPLE_HTML)
    with pytest.raises(AssertionError, match="Expected to see rendered text"):
        response.assert_see_text("Missing")


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_dont_see_text_should_pass_when_text_absent(make_response):
    response = make_response(SIMPLE_HTML)
    assert response.assert_dont_see_text("Missing") is response


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_dont_see_text_should_raise_when_text_present(make_response):
    response = make_response(SIMPLE_HTML)
    with pytest.raises(AssertionError, match="Did not expect rendered text"):
        response.assert_dont_see_text("bold text")


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_see_html_in_order_should_pass_when_fragments_appear_in_sequence(make_response):
    response = make_response(SIMPLE_HTML)
    assert response.assert_see_html_in_order(["Hello", "<strong>bold"]) is response


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_see_html_in_order_should_raise_when_fragment_absent(make_response):
    response = make_response(SIMPLE_HTML)
    with pytest.raises(AssertionError, match="HTML markup 'Missing'"):
        response.assert_see_html_in_order(["Hello", "Missing"])


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_see_html_in_order_should_raise_when_order_is_wrong(make_response):
    response = make_response(SIMPLE_HTML)
    with pytest.raises(AssertionError, match="after 'test page'"):
        response.assert_see_html_in_order(["test page", "Hello"])


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_see_text_in_order_should_pass_when_texts_appear_in_sequence(make_response):
    response = make_response(SIMPLE_HTML)
    assert response.assert_see_text_in_order(["Hello", "bold text"]) is response


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_see_text_in_order_should_raise_when_text_absent(make_response):
    response = make_response(SIMPLE_HTML)
    with pytest.raises(AssertionError, match="Rendered text 'Missing'"):
        response.assert_see_text_in_order(["Hello", "Missing"])


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_see_text_in_order_should_raise_when_order_is_wrong(make_response):
    response = make_response(SIMPLE_HTML)
    with pytest.raises(AssertionError, match="after 'bold text'"):
        response.assert_see_text_in_order(["bold text", "Hello"])


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_html_contains_should_pass_when_fragment_present_in_document(make_response):
    response = make_response(SIMPLE_HTML)
    assert response.assert_html_contains("<h1>Hello World</h1>") is response


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_html_contains_should_raise_when_fragment_absent(make_response):
    response = make_response(SIMPLE_HTML)
    with pytest.raises(AssertionError):
        response.assert_html_contains("<h1>Missing</h1>")


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_html_should_return_response_when_selector_and_callback_provided(make_response):
    response = make_response(SECTIONS_HTML)
    result = response.assert_html(
        "table#active-users",
        lambda users: users.count("tbody tr", 3).see_text("Alice"),
    )
    assert result is response


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_html_should_return_document_assertable_when_no_arguments(make_response):
    response = make_response(SECTIONS_HTML)
    assert isinstance(response.assert_html(), AssertableHtml)


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_html_should_return_scoped_assertable_when_only_selector_provided(make_response):
    response = make_response(SECTIONS_HTML)
    table = response.assert_html("table#active-users")
    assert isinstance(table, AssertableHtml)
    table.count("tbody tr", 3)


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_html_should_raise_when_selector_does_not_match(make_response):
    response = make_response(SECTIONS_HTML)
    with pytest.raises(AssertionError, match="Selector 'table#nonexistent' not found"):
        response.assert_html("table#nonexistent", lambda _: None)


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_html_should_isolate_assertions_to_scoped_section(make_response):
    response = make_response(SECTIONS_HTML)
    result = (
        response.assert_ok()
        .assert_html("section#billing", lambda s: s.see_text("alice@example.com"))
        .assert_html("section#audit-log", lambda s: s.dont_see_text("alice@example.com").see_text("bob@example.com"))
    )
    assert result is response


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_html_should_cache_parsed_document_across_calls(make_response):
    response = make_response(SECTIONS_HTML)
    assert response.assert_html() is response.assert_html()


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_html_should_not_contaminate_cache_when_alternating_root_and_scoped_calls(make_response):
    response = make_response(SECTIONS_HTML)
    result = (
        response.assert_ok()
        .assert_see_text("Dashboard")
        .assert_html("table#active-users", lambda t: t.count("tbody tr.row", 3).see_text("Alice"))
        .assert_html("section#billing", lambda s: s.see_text("alice@example.com").dont_see_text("Carol"))
        .assert_html("section#audit-log", lambda s: s.see_text("bob@example.com").dont_see_text("Alice"))
        .assert_see_text("Footer text outside the table")
    )
    assert result is response


@pytest.mark.parametrize("make_response", HTML_RESPONSE_FACTORIES)
def test_assert_html_should_not_mutate_cached_root_when_scoping(make_response):
    response = make_response(SECTIONS_HTML)
    root_before = response.assert_html()
    response.assert_html("table#active-users", lambda t: t.count("tbody tr.row", 3))
    assert response.assert_html() is root_before
    response.assert_see_text("Dashboard").assert_see_text("Footer text outside the table")
