from __future__ import annotations

import json as stdjson
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, overload

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

from pyssertive.formats.json import AssertableJson


class JsonContentAssertionsMixin:
    content: bytes
    _cached_assertable_json: AssertableJson | None = None

    @overload
    def assert_json(self) -> AssertableJson: ...
    @overload
    def assert_json(self, path: str) -> AssertableJson: ...
    @overload
    def assert_json(self, path: str, callback: Callable[[AssertableJson], Any]) -> Self: ...

    def assert_json(
        self,
        path: str | None = None,
        callback: Callable[[AssertableJson], Any] | None = None,
    ) -> Self | AssertableJson:
        cached = self._cached_assertable_json
        if cached is None:
            try:
                data = stdjson.loads(self.content)
            except stdjson.JSONDecodeError:
                raise AssertionError("Response content is not valid JSON") from None
            cached = AssertableJson(data)
            self._cached_assertable_json = cached
        scoped: AssertableJson = cached
        if path is not None:
            result = scoped.json(path)
            assert isinstance(result, AssertableJson)
            scoped = result
        if callback is not None:
            callback(scoped)
            return self
        return scoped

    def assert_json_path(self, path: str, expected: Any) -> Self:
        self.assert_json().where(path, expected)
        return self

    def assert_json_fragment(self, fragment: dict) -> Self:
        self.assert_json().fragment(fragment)
        return self

    def assert_json_missing_fragment(self, fragment: dict) -> Self:
        self.assert_json().missing_fragment(fragment)
        return self

    def assert_json_count(self, expected: int, path: str | None = None) -> Self:
        if path:
            self.assert_json(path).count(expected)
        else:
            self.assert_json().count(expected)
        return self

    def assert_exact_json(self, expected: Any) -> Self:
        self.assert_json().exact(expected)
        return self

    def assert_json_structure(self, structure: dict) -> Self:
        self.assert_json().structure(structure)
        return self

    def assert_json_missing_path(self, path: str) -> Self:
        self.assert_json().missing(path)
        return self

    def assert_json_is_dict(self) -> Self:
        self.assert_json().is_dict()
        return self

    def assert_json_is_list(self) -> Self:
        self.assert_json().is_list()
        return self

    def assert_json_schema(self, schema: dict[str, Any] | str | Path) -> Self:
        self.assert_json().matches_schema(schema)
        return self
