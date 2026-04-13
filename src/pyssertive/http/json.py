from __future__ import annotations

import json as stdjson
import sys
import urllib.request
import warnings
from collections.abc import Callable
from pathlib import Path
from typing import Any, overload

import jsonschema

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

from django.http import HttpResponse


def _resolve_schema(schema: dict[str, Any] | str | Path) -> dict[str, Any]:
    if isinstance(schema, dict):
        return schema

    raw = str(schema)

    if raw.startswith(("http://", "https://")):
        with urllib.request.urlopen(raw) as resp:
            return stdjson.loads(resp.read())

    path = Path(raw)
    if not path.is_file():
        raise FileNotFoundError(f"Schema file not found: {path}")
    with path.open() as f:
        return stdjson.load(f)


class AssertableJson:
    """
    Fluent assertions over a parsed JSON document or a scoped sub-tree.

    Created implicitly by ``FluentResponse.assert_json()``.  Scoping via
    :meth:`json` returns a new instance bound to a sub-tree of the
    already-parsed data — no re-parsing.

    All path arguments use dot-notation relative to the current scope
    (e.g. ``"user.profile.age"``).  Array indices are numeric strings
    (e.g. ``"items.0.id"``).
    """

    def __init__(self, data: Any, *, _path: str = "") -> None:
        self._data = data
        self._path = _path

    def _full_path(self, key: str) -> str:
        if self._path:
            return f"{self._path}.{key}"
        return key

    def _resolve(self, path: str) -> Any:
        current = self._data
        for part in path.split("."):
            if isinstance(current, dict):
                if part not in current:
                    raise AssertionError(f"Path '{self._full_path(path)}' not found in JSON")
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                idx = int(part)
                if idx >= len(current):
                    raise AssertionError(f"Index {idx} out of range at '{self._full_path(path)}'")
                current = current[idx]
            else:
                raise AssertionError(f"Path '{self._full_path(path)}' not traversable in JSON")
        return current

    def _path_exists(self, path: str) -> bool:
        try:
            self._resolve(path)
        except AssertionError:
            return False
        return True

    def has(self, key: str, count: int | None = None) -> Self:
        assert self._path_exists(key), f"Expected path '{self._full_path(key)}' to exist in JSON"
        if count is not None:
            value = self._resolve(key)
            assert isinstance(value, (list, dict)), (
                f"Expected '{self._full_path(key)}' to be countable, got {type(value).__name__}"
            )
            actual = len(value)
            assert actual == count, f"Expected {count} items at '{self._full_path(key)}', got {actual}"
        return self

    def missing(self, key: str) -> Self:
        if self._path_exists(key):
            value = self._resolve(key)
            raise AssertionError(f"Path '{self._full_path(key)}' should not exist but has value: {value}")
        return self

    def where(self, key: str, expected: Any) -> Self:
        actual = self._resolve(key)
        if callable(expected) and not isinstance(expected, (str, bytes, int, float, bool, list, dict, type(None))):
            assert expected(actual), f"Value at '{self._full_path(key)}' did not satisfy predicate, got: {actual!r}"
        else:
            assert actual == expected, f"Expected '{expected}' at '{self._full_path(key)}', got '{actual}'"
        return self

    def where_not(self, key: str, unexpected: Any) -> Self:
        actual = self._resolve(key)
        assert actual != unexpected, f"Expected '{self._full_path(key)}' to not be '{unexpected}', but it was"
        return self

    def where_truthy(self, key: str) -> Self:
        actual = self._resolve(key)
        assert actual, f"Expected truthy value at '{self._full_path(key)}', got '{actual}'"
        return self

    def where_falsy(self, key: str) -> Self:
        actual = self._resolve(key)
        assert not actual, f"Expected falsy value at '{self._full_path(key)}', got '{actual}'"
        return self

    def where_type(self, key: str, expected_type: type | tuple[type, ...]) -> Self:
        actual = self._resolve(key)
        if isinstance(expected_type, tuple):
            type_names = " | ".join(t.__name__ for t in expected_type)
        else:
            type_names = expected_type.__name__
        assert isinstance(actual, expected_type), (
            f"Expected type {type_names} at '{self._full_path(key)}', got {type(actual).__name__}"
        )
        return self

    def count(self, expected: int) -> Self:
        assert isinstance(self._data, (list, dict)), (
            f"Expected countable data at scope '{self._path or 'root'}', got {type(self._data).__name__}"
        )
        actual = len(self._data)
        assert actual == expected, f"Expected {expected} items at scope '{self._path or 'root'}', got {actual}"
        return self

    def fragment(self, expected: dict) -> Self:
        flat = stdjson.dumps(self._data)
        for key, value in expected.items():
            pair = f'"{key}": {stdjson.dumps(value)}'
            assert pair in flat, f"Fragment {key}: {value} not found at scope '{self._path or 'root'}'"
        return self

    def missing_fragment(self, expected: dict) -> Self:
        flat = stdjson.dumps(self._data)
        for key, value in expected.items():
            pair = f'"{key}": {stdjson.dumps(value)}'
            assert pair not in flat, f"Unexpected fragment {key}: {value} found at scope '{self._path or 'root'}'"
        return self

    def exact(self, expected: Any) -> Self:
        assert self._data == expected, f"Expected exact JSON: {expected}, got: {self._data}"
        return self

    def is_dict(self) -> Self:
        assert isinstance(self._data, dict), (
            f"Expected JSON dict at scope '{self._path or 'root'}', got {type(self._data).__name__}"
        )
        return self

    def is_list(self) -> Self:
        assert isinstance(self._data, list), (
            f"Expected JSON list at scope '{self._path or 'root'}', got {type(self._data).__name__}"
        )
        return self

    def structure(self, schema: dict) -> Self:
        assert isinstance(self._data, dict), (
            f"Expected JSON dict at scope '{self._path or 'root'}', got {type(self._data).__name__}"
        )
        for key, expected_type in schema.items():
            assert key in self._data, f"Key '{key}' missing from JSON at scope '{self._path or 'root'}'"
            if expected_type is not None:
                actual_type = type(self._data[key])
                assert isinstance(self._data[key], expected_type), (
                    f"Key '{key}' expected type {expected_type.__name__}, got {actual_type.__name__}"
                )
        return self

    def matches_schema(self, schema: dict[str, Any] | str | Path) -> Self:
        resolved = _resolve_schema(schema)
        try:
            jsonschema.validate(instance=self._data, schema=resolved)
        except jsonschema.ValidationError as exc:
            path_str = ".".join(str(p) for p in exc.absolute_path) if exc.absolute_path else "root"
            scope = f" at scope '{self._path}'" if self._path else ""
            raise AssertionError(f"JSON schema validation failed{scope} at '{path_str}': {exc.message}") from None
        return self

    def json(
        self,
        path: str,
        callback: Callable[[AssertableJson], Any] | None = None,
    ) -> AssertableJson | Self:
        data = self._resolve(path)
        child = AssertableJson(data, _path=self._full_path(path))
        if callback is None:
            return child
        callback(child)
        return self


_DEPRECATED_IS_OBJECT_MSG = (
    "assert_json_is_object() is deprecated and will be removed in a future release. Use assert_json_is_dict() instead."
)
_DEPRECATED_IS_ARRAY_MSG = (
    "assert_json_is_array() is deprecated and will be removed in a future release. Use assert_json_is_list() instead."
)


class JsonContentAssertionsMixin:
    _response: HttpResponse
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
                data = stdjson.loads(self._response.content)
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

    def assert_json_is_object(self) -> Self:
        warnings.warn(_DEPRECATED_IS_OBJECT_MSG, DeprecationWarning, stacklevel=2)
        return self.assert_json_is_dict()

    def assert_json_is_array(self) -> Self:
        warnings.warn(_DEPRECATED_IS_ARRAY_MSG, DeprecationWarning, stacklevel=2)
        return self.assert_json_is_list()
