from __future__ import annotations

import html as html_lib
import re
import sys
import warnings
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, overload

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

from bs4 import BeautifulSoup, NavigableString

from pyssertive.protocol import HttpResponseProtocol

if TYPE_CHECKING:
    from bs4 import Tag


_WS = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return _WS.sub(" ", html_lib.unescape(text)).strip()


def _normalize_attrs(tag: Any) -> dict[str, Any]:
    """Return tag attributes in a comparable, order-insensitive form.

    Multi-valued attributes (e.g. ``class``) are stored by BeautifulSoup
    as ``list[str]``; converting to ``frozenset`` makes attribute equality
    insensitive to value order (``class="a b"`` matches ``class="b a"``).
    """
    out: dict[str, Any] = {}
    for key, value in tag.attrs.items():
        out[key] = frozenset(value) if isinstance(value, list) else value
    return out


def _meaningful_children(tag: Any) -> list[Any]:
    """Return a tag's children with whitespace-only text nodes dropped."""
    result: list[Any] = []
    for child in tag.children:
        if isinstance(child, NavigableString):
            if str(child).strip():
                result.append(child)
        else:
            result.append(child)
    return result


def _tags_equivalent(needle: Any, candidate: Any) -> bool:
    """Recursively test semantic equivalence between two HTML elements.

    Two elements are equivalent when they share tag name, attribute set
    (order-insensitive, with multi-valued attributes compared as sets),
    and children. Whitespace-only text nodes are ignored; remaining text
    content is whitespace-normalized before comparison.
    """
    if isinstance(needle, NavigableString):
        if not isinstance(candidate, NavigableString):
            return False
        return _normalize(str(needle)) == _normalize(str(candidate))

    if isinstance(candidate, NavigableString):
        return False

    if needle.name != candidate.name:
        return False
    if _normalize_attrs(needle) != _normalize_attrs(candidate):
        return False

    needle_children = _meaningful_children(needle)
    candidate_children = _meaningful_children(candidate)
    if len(needle_children) != len(candidate_children):
        return False
    return all(_tags_equivalent(n, c) for n, c in zip(needle_children, candidate_children, strict=True))


def _html_contains_fragment(haystack: Any, fragment: str) -> bool:
    """Check whether ``haystack`` contains ``fragment`` as a semantic subtree.

    Replaces ``django.test.SimpleTestCase.assertInHTML`` with a pure-BS4
    implementation so the core remains framework-agnostic.
    """
    soup = BeautifulSoup(fragment, "html.parser")
    roots = _meaningful_children(soup)
    if not roots:
        return True

    if all(isinstance(r, NavigableString) for r in roots):
        needle_text = _normalize(" ".join(str(r) for r in roots))
        return needle_text in _normalize(haystack.get_text(" "))

    first = roots[0]
    if isinstance(first, NavigableString):
        return _normalize(str(first)) in _normalize(haystack.get_text(" "))

    if len(roots) == 1:
        return any(_tags_equivalent(first, candidate) for candidate in haystack.find_all(first.name))

    # Multi-root fragment: roots must appear as consecutive siblings.
    for candidate in haystack.find_all(first.name):
        if not _tags_equivalent(first, candidate):
            continue
        parent = candidate.parent
        if parent is None:  # pragma: no cover — BS4 find_all results always have a parent
            continue
        siblings = _meaningful_children(parent)
        idx = siblings.index(candidate)
        window = siblings[idx : idx + len(roots)]
        if len(window) == len(roots) and all(_tags_equivalent(n, s) for n, s in zip(roots, window, strict=True)):
            return True
    return False


class AssertableHtml:
    """
    Fluent assertions over an HTML document or a scoped sub-tree.

    Created implicitly by ``FluentResponse.assert_html()``. Scoping via
    :meth:`html` returns a new instance bound to a sub-tree of the
    already-parsed document — no re-parsing.

    Two families of content assertions:

    * ``see_html`` / ``dont_see_html`` — operate on the raw HTML markup
      (tags preserved). Use when asserting tag structure, class names,
      attribute values, or specific HTML fragments.
    * ``see_text`` / ``dont_see_text`` — operate on the rendered visible
      text (tags stripped). Use when asserting what a reader would see.

    Selector-based assertions (``count``, ``exists``, ``missing``, ``html``)
    use CSS selectors via BeautifulSoup/soupsieve.
    """

    def __init__(self, markup: str, *, _tag: Tag | None = None, _scope: str = "document") -> None:
        self._markup = markup
        self._tag: Any = _tag if _tag is not None else BeautifulSoup(markup, "html.parser")
        self._scope = _scope

    def _raw(self) -> str:
        return _normalize(self._markup)

    def _text(self) -> str:
        return _normalize(self._tag.get_text(" "))

    def _child_scope(self, selector: str) -> str:
        if self._scope == "document":
            return selector
        return f"{self._scope} > {selector}"

    def see_html(self, fragment: str) -> Self:
        markup = self._raw()
        assert fragment in markup, f"Expected to see HTML markup '{fragment}' in scope '{self._scope}', got: {markup}"
        return self

    def dont_see_html(self, fragment: str) -> Self:
        markup = self._raw()
        assert fragment not in markup, (
            f"Did not expect HTML markup '{fragment}' in scope '{self._scope}', got: {markup}"
        )
        return self

    def see_html_in_order(self, fragments: list[str]) -> Self:
        markup = self._raw()
        last_index = -1
        last_fragment = ""
        for key, fragment in enumerate(fragments):
            index = markup.find(fragment, last_index + 1)
            location = "" if last_fragment == "" else f"after '{last_fragment}'"
            assert index != -1, f"HTML markup '{fragment}' ({key}) not found {location} in scope '{self._scope}'"
            last_index = index
            last_fragment = fragment
        return self

    def see_text(self, text: str) -> Self:
        plain = self._text()
        assert text in plain, f"Expected to see rendered text '{text}' in scope '{self._scope}', got: {plain}"
        return self

    def dont_see_text(self, text: str) -> Self:
        plain = self._text()
        assert text not in plain, f"Did not expect rendered text '{text}' in scope '{self._scope}', got: {plain}"
        return self

    def see_text_in_order(self, texts: list[str]) -> Self:
        plain = self._text()
        last_index = -1
        last_text = ""
        for key, text in enumerate(texts):
            index = plain.find(text, last_index + 1)
            location = "" if last_text == "" else f"after '{last_text}'"
            assert index != -1, f"Rendered text '{text}' ({key}) not found {location} in scope '{self._scope}'"
            last_index = index
            last_text = text
        return self

    def html_contains(self, fragment: str) -> Self:
        assert _html_contains_fragment(self._tag, fragment), (
            f"HTML fragment '{fragment}' not found in scope '{self._scope}'"
        )
        return self

    def count(self, selector: str, expected: int) -> Self:
        actual = len(self._tag.select(selector))
        assert actual == expected, (
            f"Expected {expected} elements matching '{selector}' in scope '{self._scope}', got {actual}"
        )
        return self

    def exists(self, selector: str) -> Self:
        assert self._tag.select_one(selector) is not None, (
            f"Expected at least one element matching '{selector}' in scope '{self._scope}'"
        )
        return self

    def missing(self, selector: str) -> Self:
        assert self._tag.select_one(selector) is None, (
            f"Expected no elements matching '{selector}' in scope '{self._scope}'"
        )
        return self

    def html(
        self,
        selector: str,
        callback: Callable[[AssertableHtml], Any] | None = None,
    ) -> AssertableHtml | Self:
        tag = self._tag.select_one(selector)
        assert tag is not None, f"Selector '{selector}' not found in scope '{self._scope}'"
        child = AssertableHtml(str(tag), _tag=tag, _scope=self._child_scope(selector))
        if callback is None:
            return child
        callback(child)
        return self


_DEPRECATED_SEE_MSG = (
    "assert_see() is deprecated and will be removed in a future release. "
    "Use assert_see_html() for HTML-markup assertions or assert_see_text() "
    "for rendered-text assertions."
)
_DEPRECATED_DONT_SEE_MSG = (
    "assert_dont_see() is deprecated and will be removed in a future release. "
    "Use assert_dont_see_html() for HTML-markup assertions or assert_dont_see_text() "
    "for rendered-text assertions."
)
_DEPRECATED_SEE_IN_ORDER_MSG = (
    "assert_see_in_order() is deprecated and will be removed in a future release. "
    "Use assert_see_html_in_order() for HTML-markup assertions or "
    "assert_see_text_in_order() for rendered-text assertions."
)


class HTMLContentAssertionsMixin:
    _response: HttpResponseProtocol
    _cached_assertable_html: AssertableHtml | None = None

    @overload
    def assert_html(self) -> AssertableHtml: ...
    @overload
    def assert_html(self, selector: str) -> AssertableHtml: ...
    @overload
    def assert_html(self, selector: str, callback: Callable[[AssertableHtml], Any]) -> Self: ...

    def assert_html(
        self,
        selector: str | None = None,
        callback: Callable[[AssertableHtml], Any] | None = None,
    ) -> Self | AssertableHtml:
        cached = self._cached_assertable_html
        if cached is None:
            body = self._response.content.decode("utf-8", errors="replace")
            cached = AssertableHtml(body)
            self._cached_assertable_html = cached
        scoped: AssertableHtml = cached
        if selector is not None:
            result = scoped.html(selector)
            assert isinstance(result, AssertableHtml)
            scoped = result
        if callback is not None:
            callback(scoped)
            return self
        return scoped

    def assert_see_html(self, fragment: str) -> Self:
        self.assert_html().see_html(fragment)
        return self

    def assert_dont_see_html(self, fragment: str) -> Self:
        self.assert_html().dont_see_html(fragment)
        return self

    def assert_see_html_in_order(self, fragments: list[str]) -> Self:
        self.assert_html().see_html_in_order(fragments)
        return self

    def assert_see_text(self, text: str) -> Self:
        self.assert_html().see_text(text)
        return self

    def assert_dont_see_text(self, text: str) -> Self:
        self.assert_html().dont_see_text(text)
        return self

    def assert_see_text_in_order(self, texts: list[str]) -> Self:
        self.assert_html().see_text_in_order(texts)
        return self

    def assert_html_contains(self, html_fragment: str) -> Self:
        self.assert_html().html_contains(html_fragment)
        return self

    def assert_see(self, text: str) -> Self:
        warnings.warn(_DEPRECATED_SEE_MSG, DeprecationWarning, stacklevel=2)
        return self.assert_see_html(text)

    def assert_dont_see(self, text: str) -> Self:
        warnings.warn(_DEPRECATED_DONT_SEE_MSG, DeprecationWarning, stacklevel=2)
        return self.assert_dont_see_html(text)

    def assert_see_in_order(self, texts: list[str]) -> Self:
        warnings.warn(_DEPRECATED_SEE_IN_ORDER_MSG, DeprecationWarning, stacklevel=2)
        return self.assert_see_html_in_order(texts)
