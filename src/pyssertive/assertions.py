from __future__ import annotations

import re
import sys
from collections.abc import Callable
from typing import Any

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

_MISSING: Any = object()


class AssertableValue:
    """
    Fluent assertions over an arbitrary Python value.

    Created directly or via the :func:`expect` factory. Methods return
    ``Self`` to allow chaining. Use :meth:`each` to apply matchers to every
    element of an iterable, and :meth:`sequence` to match elements positionally.
    """

    def __init__(self, value: Any) -> None:
        self._value = value

    def equals(self, expected: Any) -> Self:
        assert self._value == expected, f"Expected value to equal {expected!r}, got {self._value!r}"
        return self

    def does_not_equal(self, unexpected: Any) -> Self:
        assert self._value != unexpected, f"Expected value to not equal {unexpected!r}"
        return self

    def is_same_as(self, expected: Any) -> Self:
        assert self._value is expected, f"Expected value to be the same instance as {expected!r}"
        return self

    def is_not_same_as(self, unexpected: Any) -> Self:
        assert self._value is not unexpected, f"Expected value to not be the same instance as {unexpected!r}"
        return self

    def is_none(self) -> Self:
        assert self._value is None, f"Expected value to be None, got {self._value!r}"
        return self

    def is_not_none(self) -> Self:
        assert self._value is not None, "Expected value to not be None"
        return self

    def is_truthy(self) -> Self:
        assert self._value, f"Expected value to be truthy, got {self._value!r}"
        return self

    def is_falsy(self) -> Self:
        assert not self._value, f"Expected value to be falsy, got {self._value!r}"
        return self

    def is_true(self) -> Self:
        assert self._value is True, f"Expected value to be True, got {self._value!r}"
        return self

    def is_false(self) -> Self:
        assert self._value is False, f"Expected value to be False, got {self._value!r}"
        return self

    def is_instance_of(self, cls: type | tuple[type, ...]) -> Self:
        type_names = " | ".join(t.__name__ for t in cls) if isinstance(cls, tuple) else cls.__name__
        assert isinstance(self._value, cls), (
            f"Expected value to be instance of {type_names}, got {type(self._value).__name__}"
        )
        return self

    def is_not_instance_of(self, cls: type | tuple[type, ...]) -> Self:
        type_names = " | ".join(t.__name__ for t in cls) if isinstance(cls, tuple) else cls.__name__
        assert not isinstance(self._value, cls), f"Expected value to not be instance of {type_names}"
        return self

    def is_type(self, cls: type) -> Self:
        assert type(self._value) is cls, (
            f"Expected value to be of exact type {cls.__name__}, got {type(self._value).__name__}"
        )
        return self

    def is_greater_than(self, other: Any) -> Self:
        assert self._value > other, f"Expected value to be greater than {other!r}, got {self._value!r}"
        return self

    def is_less_than(self, other: Any) -> Self:
        assert self._value < other, f"Expected value to be less than {other!r}, got {self._value!r}"
        return self

    def is_at_least(self, other: Any) -> Self:
        assert self._value >= other, f"Expected value to be at least {other!r}, got {self._value!r}"
        return self

    def is_at_most(self, other: Any) -> Self:
        assert self._value <= other, f"Expected value to be at most {other!r}, got {self._value!r}"
        return self

    def is_between(self, low: Any, high: Any) -> Self:
        assert low <= self._value <= high, (
            f"Expected value to be between {low!r} and {high!r} (inclusive), got {self._value!r}"
        )
        return self

    def has_count(self, expected: int) -> Self:
        actual = len(self._value)
        assert actual == expected, f"Expected count of {expected}, got {actual}"
        return self

    def is_empty(self) -> Self:
        assert len(self._value) == 0, f"Expected value to be empty, got {self._value!r}"
        return self

    def is_not_empty(self) -> Self:
        assert len(self._value) > 0, "Expected value to not be empty"
        return self

    def contains(self, *items: Any) -> Self:
        for item in items:
            assert item in self._value, f"Expected value to contain {item!r}"
        return self

    def does_not_contain(self, *items: Any) -> Self:
        for item in items:
            assert item not in self._value, f"Expected value to not contain {item!r}"
        return self

    def has_key(self, key: str) -> Self:
        assert isinstance(self._value, dict), f"Expected a dict, got {type(self._value).__name__}"
        assert key in self._value, f"Expected dict to have key {key!r}"
        return self

    def does_not_have_key(self, key: str) -> Self:
        assert isinstance(self._value, dict), f"Expected a dict, got {type(self._value).__name__}"
        assert key not in self._value, f"Expected dict to not have key {key!r}"
        return self

    def has_keys(self, *keys: str) -> Self:
        assert isinstance(self._value, dict), f"Expected a dict, got {type(self._value).__name__}"
        for key in keys:
            assert key in self._value, f"Expected dict to have key {key!r}"
        return self

    def has_attribute(self, name: str, value: Any = _MISSING) -> Self:
        assert hasattr(self._value, name), f"Expected object to have attribute {name!r}"
        if value is not _MISSING:
            actual = getattr(self._value, name)
            assert actual == value, f"Expected attribute {name!r} to equal {value!r}, got {actual!r}"
        return self

    def does_not_have_attribute(self, name: str) -> Self:
        assert not hasattr(self._value, name), f"Expected object to not have attribute {name!r}"
        return self

    def matches(self, pattern: str) -> Self:
        assert re.search(pattern, self._value) is not None, f"Expected {self._value!r} to match pattern '{pattern}'"
        return self

    def does_not_match(self, pattern: str) -> Self:
        assert re.search(pattern, self._value) is None, f"Expected {self._value!r} to not match pattern '{pattern}'"
        return self

    def starts_with(self, prefix: str) -> Self:
        assert self._value.startswith(prefix), f"Expected {self._value!r} to start with {prefix!r}"
        return self

    def ends_with(self, suffix: str) -> Self:
        assert self._value.endswith(suffix), f"Expected {self._value!r} to end with {suffix!r}"
        return self

    def each(self) -> _Each:
        assert hasattr(self._value, "__iter__"), f"Expected an iterable, got {type(self._value).__name__}"
        return _Each(self._value)

    def sequence(self, *expected: Any) -> Self:
        assert hasattr(self._value, "__iter__"), f"Expected an iterable, got {type(self._value).__name__}"
        items = list(self._value)
        assert len(items) == len(expected), f"Expected sequence of length {len(expected)}, got {len(items)}"
        for item, exp in zip(items, expected, strict=True):
            sub = AssertableValue(item)
            if callable(exp):
                exp(sub)
            else:
                sub.equals(exp)
        return self


class _Each:
    def __init__(self, items: Any) -> None:
        self._items = list(items)

    def __getattr__(self, name: str) -> Callable[..., _Each]:
        def apply(*args: Any, **kwargs: Any) -> _Each:
            for item in self._items:
                getattr(AssertableValue(item), name)(*args, **kwargs)
            return self

        return apply


def expect(value: Any) -> AssertableValue:
    return AssertableValue(value)
