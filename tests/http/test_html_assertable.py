from __future__ import annotations

import re

import pytest

from pyssertive.http.html import AssertableHtml

SAMPLE = """<!DOCTYPE html>
<html>
<head><title>Sample</title></head>
<body>
<h1>Report</h1>
<section id="summary">
  <h2>Summary</h2>
  <p>Total: <span class="currency">$100</span></p>
</section>
<section id="orders">
  <h2>Orders</h2>
  <table class="orders">
    <thead><tr><th>Id</th><th>Status</th></tr></thead>
    <tbody>
      <tr class="order"><td>ORD-1</td><td>Shipped</td></tr>
      <tr class="order"><td>ORD-2</td><td>Shipped</td></tr>
      <tr class="order"><td>ORD-3</td><td>Pending</td></tr>
    </tbody>
  </table>
</section>
<footer>Rendered &amp; delivered</footer>
</body>
</html>"""


@pytest.fixture
def doc() -> AssertableHtml:
    return AssertableHtml(SAMPLE)


def test_see_html_should_match_when_tag_markup_present(doc: AssertableHtml):
    doc.see_html("<h1>Report</h1>")


def test_see_html_should_match_against_unescaped_entities(doc: AssertableHtml):
    doc.see_html("Rendered & delivered")


def test_see_html_should_mention_scope_in_error_message(doc: AssertableHtml):
    with pytest.raises(AssertionError, match="in scope 'document'"):
        doc.see_html("not present")


def test_dont_see_html_should_pass_when_markup_absent(doc: AssertableHtml):
    doc.dont_see_html("<h1>Missing</h1>")


def test_dont_see_html_should_raise_when_markup_present(doc: AssertableHtml):
    with pytest.raises(AssertionError, match="Did not expect HTML markup"):
        doc.dont_see_html("<h1>Report</h1>")


def test_see_html_in_order_should_pass_when_fragments_appear_in_sequence(doc: AssertableHtml):
    doc.see_html_in_order(["<h1>", "Summary", "Orders", "<footer>"])


def test_see_html_in_order_should_raise_when_fragment_absent(doc: AssertableHtml):
    with pytest.raises(AssertionError, match="HTML markup 'Ghost'"):
        doc.see_html_in_order(["Summary", "Ghost"])


def test_see_text_should_match_against_rendered_text(doc: AssertableHtml):
    doc.see_text("Total: $100")


def test_see_text_should_not_match_against_html_tags(doc: AssertableHtml):
    with pytest.raises(AssertionError, match="Expected to see rendered text"):
        doc.see_text("<h1>")


def test_dont_see_text_should_pass_when_text_absent(doc: AssertableHtml):
    doc.dont_see_text("This string is definitely absent")


def test_dont_see_text_should_raise_when_text_present(doc: AssertableHtml):
    with pytest.raises(AssertionError, match="Did not expect rendered text"):
        doc.dont_see_text("Report")


def test_see_text_in_order_should_pass_when_texts_appear_in_sequence(doc: AssertableHtml):
    doc.see_text_in_order(["Report", "Summary", "Orders", "Rendered"])


def test_see_text_in_order_should_raise_when_text_order_is_wrong(doc: AssertableHtml):
    with pytest.raises(AssertionError, match="after 'Orders'"):
        doc.see_text_in_order(["Orders", "Summary"])


def test_html_contains_should_pass_when_fragment_is_found(doc: AssertableHtml):
    doc.html_contains("<h1>Report</h1>")


def test_html_contains_should_raise_when_fragment_is_absent(doc: AssertableHtml):
    with pytest.raises(AssertionError):
        doc.html_contains("<h1>Missing</h1>")


def test_html_contains_should_be_attribute_order_insensitive():
    doc = AssertableHtml('<a href="/home" class="btn">go</a>')

    doc.html_contains('<a class="btn" href="/home">go</a>')


def test_html_contains_should_be_class_order_insensitive():
    doc = AssertableHtml('<span class="alpha beta gamma">x</span>')

    doc.html_contains('<span class="gamma alpha beta">x</span>')


def test_html_contains_should_normalize_whitespace_in_text():
    doc = AssertableHtml("<p>Hello   world\n  again</p>")

    doc.html_contains("<p>Hello world again</p>")


def test_html_contains_should_ignore_insignificant_whitespace_between_children():
    doc = AssertableHtml("<ul>\n  <li>one</li>\n  <li>two</li>\n</ul>")

    doc.html_contains("<ul><li>one</li><li>two</li></ul>")


def test_html_contains_should_reject_when_attributes_differ():
    doc = AssertableHtml('<a href="/home" class="btn">go</a>')

    with pytest.raises(AssertionError):
        doc.html_contains('<a href="/away" class="btn">go</a>')


def test_html_contains_should_reject_extra_children_in_candidate():
    doc = AssertableHtml("<ul><li>one</li><li>two</li></ul>")

    with pytest.raises(AssertionError):
        doc.html_contains("<ul><li>one</li></ul>")


def test_html_contains_should_match_plain_text_fragment():
    doc = AssertableHtml("<p>Rendered &amp; delivered</p>")

    doc.html_contains("Rendered & delivered")


def test_html_contains_should_match_multi_root_fragment_in_sibling_order():
    doc = AssertableHtml("<div><h1>Title</h1><p>Body</p><footer>End</footer></div>")

    doc.html_contains("<h1>Title</h1><p>Body</p>")


def test_html_contains_should_reject_multi_root_fragment_in_wrong_order():
    doc = AssertableHtml("<div><h1>Title</h1><p>Body</p></div>")

    with pytest.raises(AssertionError):
        doc.html_contains("<p>Body</p><h1>Title</h1>")


def test_html_contains_should_pass_for_empty_fragment(doc: AssertableHtml):
    doc.html_contains("")


def test_html_contains_should_reject_when_tag_names_differ():
    doc = AssertableHtml("<div><p>x</p></div>")

    with pytest.raises(AssertionError):
        doc.html_contains("<div><span>x</span></div>")


def test_html_contains_should_reject_when_needle_text_position_holds_a_tag():
    doc = AssertableHtml("<div><b>text</b><span>x</span></div>")

    with pytest.raises(AssertionError):
        doc.html_contains("<div>text<span>x</span></div>")


def test_html_contains_should_reject_when_needle_tag_position_holds_text():
    doc = AssertableHtml("<div>text<span>x</span></div>")

    with pytest.raises(AssertionError):
        doc.html_contains("<div><b>text</b><span>x</span></div>")


def test_html_contains_should_match_mixed_text_and_tag_fragment():
    doc = AssertableHtml("<p>Hello <b>world</b></p>")

    doc.html_contains("Hello <b>world</b>")


def test_html_contains_should_skip_non_matching_first_root_in_multi_root_search():
    doc = AssertableHtml("<div><h1>Other</h1><p>noise</p><h1>Title</h1><p>Body</p></div>")

    doc.html_contains("<h1>Title</h1><p>Body</p>")


def test_count_should_pass_when_element_count_matches(doc: AssertableHtml):
    doc.count("tbody tr.order", 3)


def test_count_should_raise_with_actual_count_when_mismatch(doc: AssertableHtml):
    with pytest.raises(AssertionError, match=r"Expected 5 elements matching 'tbody tr\.order'.*got 3"):
        doc.count("tbody tr.order", 5)


def test_exists_should_pass_when_selector_matches(doc: AssertableHtml):
    doc.exists("table.orders thead th")


def test_exists_should_raise_when_selector_does_not_match(doc: AssertableHtml):
    with pytest.raises(AssertionError, match=r"Expected at least one element matching 'div\.absent'"):
        doc.exists("div.absent")


def test_missing_should_pass_when_selector_does_not_match(doc: AssertableHtml):
    doc.missing("div.sidebar")


def test_missing_should_raise_when_selector_matches(doc: AssertableHtml):
    with pytest.raises(AssertionError, match="Expected no elements matching 'h1'"):
        doc.missing("h1")


def test_html_should_return_self_when_callback_provided(doc: AssertableHtml):
    result = doc.html("section#summary", lambda s: s.see_text("Total"))
    assert result is doc


def test_html_should_return_new_scoped_assertable_when_no_callback(doc: AssertableHtml):
    scoped = doc.html("section#orders")
    assert isinstance(scoped, AssertableHtml)
    assert scoped is not doc
    scoped.count("tr.order", 3)


def test_html_should_scope_assertions_to_matched_subtree(doc: AssertableHtml):
    doc.html("section#summary", lambda s: s.see_text("Total: $100").dont_see_text("Orders"))


def test_html_should_support_nested_scoping(doc: AssertableHtml):
    doc.html(
        "section#orders",
        lambda orders: orders.count("tr.order", 3).html(
            "tr.order:first-child", lambda row: row.see_text("ORD-1").see_text("Shipped")
        ),
    )


def test_html_should_include_parent_scope_in_nested_error_path(doc: AssertableHtml):
    with pytest.raises(AssertionError, match=re.escape("scope 'section#orders > tr.order:first-child'")):
        doc.html(
            "section#orders", lambda orders: orders.html("tr.order:first-child", lambda row: row.see_text("Ghost"))
        )


def test_html_should_raise_when_selector_does_not_match_in_scope(doc: AssertableHtml):
    with pytest.raises(AssertionError, match="Selector 'section#nonexistent' not found in scope 'document'"):
        doc.html("section#nonexistent", lambda _: None)


def test_html_should_isolate_count_to_scope(doc: AssertableHtml):
    doc.html("section#summary", lambda s: s.count("h2", 1))
    doc.html("section#orders", lambda s: s.count("h2", 1))
    doc.count("h2", 2)


def test_html_should_isolate_dont_see_text_to_scope(doc: AssertableHtml):
    doc.html("section#summary", lambda s: s.dont_see_text("Shipped"))


def test_see_html_should_return_self_for_method_chaining(doc: AssertableHtml):
    assert doc.see_html("Report") is doc


def test_dont_see_html_should_return_self_for_method_chaining(doc: AssertableHtml):
    assert doc.dont_see_html("Ghost") is doc


def test_count_should_return_self_for_method_chaining(doc: AssertableHtml):
    assert doc.count("h1", 1) is doc


def test_exists_should_return_self_for_method_chaining(doc: AssertableHtml):
    assert doc.exists("h1") is doc


def test_missing_should_return_self_for_method_chaining(doc: AssertableHtml):
    assert doc.missing("div.absent") is doc


def test_html_contains_should_return_self_for_method_chaining(doc: AssertableHtml):
    assert doc.html_contains("<h1>Report</h1>") is doc


def test_see_text_should_return_self_for_method_chaining(doc: AssertableHtml):
    assert doc.see_text("Report") is doc


def test_dont_see_text_should_return_self_for_method_chaining(doc: AssertableHtml):
    assert doc.dont_see_text("Ghost") is doc


def test_see_html_in_order_should_return_self_for_method_chaining(doc: AssertableHtml):
    assert doc.see_html_in_order(["Report", "Summary"]) is doc


def test_see_text_in_order_should_return_self_for_method_chaining(doc: AssertableHtml):
    assert doc.see_text_in_order(["Report", "Summary"]) is doc
