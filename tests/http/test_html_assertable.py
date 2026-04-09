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


def test_see_html_matches_tags(doc: AssertableHtml) -> None:
    doc.see_html("<h1>Report</h1>")


def test_see_html_unescapes_entities(doc: AssertableHtml) -> None:
    # The raw markup has &amp;; after unescape it becomes &.
    doc.see_html("Rendered & delivered")


def test_see_html_error_mentions_scope(doc: AssertableHtml) -> None:
    with pytest.raises(AssertionError, match="in scope 'document'"):
        doc.see_html("not present")


def test_dont_see_html_passes(doc: AssertableHtml) -> None:
    doc.dont_see_html("<h1>Missing</h1>")


def test_dont_see_html_fails(doc: AssertableHtml) -> None:
    with pytest.raises(AssertionError, match="Did not expect HTML markup"):
        doc.dont_see_html("<h1>Report</h1>")


def test_see_html_in_order_passes(doc: AssertableHtml) -> None:
    doc.see_html_in_order(["<h1>", "Summary", "Orders", "<footer>"])


def test_see_html_in_order_reports_missing(doc: AssertableHtml) -> None:
    with pytest.raises(AssertionError, match="HTML markup 'Ghost'"):
        doc.see_html_in_order(["Summary", "Ghost"])


def test_see_text_strips_tags(doc: AssertableHtml) -> None:
    doc.see_text("Total: $100")


def test_see_text_does_not_match_tags(doc: AssertableHtml) -> None:
    with pytest.raises(AssertionError, match="Expected to see rendered text"):
        doc.see_text("<h1>")


def test_dont_see_text_passes(doc: AssertableHtml) -> None:
    doc.dont_see_text("This string is definitely absent")


def test_dont_see_text_fails(doc: AssertableHtml) -> None:
    with pytest.raises(AssertionError, match="Did not expect rendered text"):
        doc.dont_see_text("Report")


def test_see_text_in_order_passes(doc: AssertableHtml) -> None:
    doc.see_text_in_order(["Report", "Summary", "Orders", "Rendered"])


def test_see_text_in_order_reports_wrong_order(doc: AssertableHtml) -> None:
    with pytest.raises(AssertionError, match="after 'Orders'"):
        doc.see_text_in_order(["Orders", "Summary"])


def test_html_contains_passes(doc: AssertableHtml) -> None:
    doc.html_contains("<h1>Report</h1>")


def test_html_contains_fails(doc: AssertableHtml) -> None:
    with pytest.raises(AssertionError):
        doc.html_contains("<h1>Missing</h1>")


def test_count_passes(doc: AssertableHtml) -> None:
    doc.count("tbody tr.order", 3)


def test_count_fails_reports_actual(doc: AssertableHtml) -> None:
    with pytest.raises(AssertionError, match=r"Expected 5 elements matching 'tbody tr\.order'.*got 3"):
        doc.count("tbody tr.order", 5)


def test_exists_passes(doc: AssertableHtml) -> None:
    doc.exists("table.orders thead th")


def test_exists_fails(doc: AssertableHtml) -> None:
    with pytest.raises(AssertionError, match=r"Expected at least one element matching 'div\.absent'"):
        doc.exists("div.absent")


def test_missing_passes(doc: AssertableHtml) -> None:
    doc.missing("div.sidebar")


def test_missing_fails(doc: AssertableHtml) -> None:
    with pytest.raises(AssertionError, match="Expected no elements matching 'h1'"):
        doc.missing("h1")


def test_html_scoping_with_callback_returns_self(doc: AssertableHtml) -> None:
    result = doc.html("section#summary", lambda s: s.see_text("Total"))
    assert result is doc


def test_html_scoping_without_callback_returns_new_scope(doc: AssertableHtml) -> None:
    scoped = doc.html("section#orders")
    assert isinstance(scoped, AssertableHtml)
    assert scoped is not doc
    scoped.count("tr.order", 3)


def test_html_scoping_scopes_content_properly(doc: AssertableHtml) -> None:
    doc.html("section#summary", lambda s: s.see_text("Total: $100").dont_see_text("Orders"))


def test_html_scoping_nested(doc: AssertableHtml) -> None:
    doc.html(
        "section#orders",
        lambda orders: orders.count("tr.order", 3).html(
            "tr.order:first-child", lambda row: row.see_text("ORD-1").see_text("Shipped")
        ),
    )


def test_html_scoping_child_scope_path_includes_parent(doc: AssertableHtml) -> None:
    with pytest.raises(AssertionError, match=re.escape("scope 'section#orders > tr.order:first-child'")):
        doc.html(
            "section#orders", lambda orders: orders.html("tr.order:first-child", lambda row: row.see_text("Ghost"))
        )


def test_html_scoping_missing_selector(doc: AssertableHtml) -> None:
    with pytest.raises(AssertionError, match="Selector 'section#nonexistent' not found in scope 'document'"):
        doc.html("section#nonexistent", lambda _: None)


def test_html_scoping_count_inside_scope(doc: AssertableHtml) -> None:
    # count inside a scope should only see elements within that scope,
    # not the whole document
    doc.html("section#summary", lambda s: s.count("h2", 1))
    doc.html("section#orders", lambda s: s.count("h2", 1))
    doc.count("h2", 2)  # but at document level we see both


def test_html_scoping_dont_see_text_isolated_to_scope(doc: AssertableHtml) -> None:
    # 'Shipped' appears in the orders table but not in summary.
    # A scoped dont_see_text on summary must pass even though 'Shipped'
    # exists elsewhere in the document.
    doc.html("section#summary", lambda s: s.dont_see_text("Shipped"))


def test_see_html_returns_self_for_chaining(doc: AssertableHtml) -> None:
    assert doc.see_html("Report") is doc


def test_dont_see_html_returns_self_for_chaining(doc: AssertableHtml) -> None:
    assert doc.dont_see_html("Ghost") is doc


def test_count_returns_self_for_chaining(doc: AssertableHtml) -> None:
    assert doc.count("h1", 1) is doc


def test_exists_returns_self_for_chaining(doc: AssertableHtml) -> None:
    assert doc.exists("h1") is doc


def test_missing_returns_self_for_chaining(doc: AssertableHtml) -> None:
    assert doc.missing("div.absent") is doc


def test_html_contains_returns_self_for_chaining(doc: AssertableHtml) -> None:
    assert doc.html_contains("<h1>Report</h1>") is doc


def test_see_text_returns_self_for_chaining(doc: AssertableHtml) -> None:
    assert doc.see_text("Report") is doc


def test_dont_see_text_returns_self_for_chaining(doc: AssertableHtml) -> None:
    assert doc.dont_see_text("Ghost") is doc


def test_see_html_in_order_returns_self_for_chaining(doc: AssertableHtml) -> None:
    assert doc.see_html_in_order(["Report", "Summary"]) is doc


def test_see_text_in_order_returns_self_for_chaining(doc: AssertableHtml) -> None:
    assert doc.see_text_in_order(["Report", "Summary"]) is doc
