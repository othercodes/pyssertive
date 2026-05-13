from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Any, overload

from pyssertive.formats.html import AssertableHtml

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self


class HTMLContentAssertionsMixin:
    content: bytes
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
            body = self.content.decode("utf-8", errors="replace")
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
