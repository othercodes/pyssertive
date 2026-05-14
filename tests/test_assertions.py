from __future__ import annotations

import pytest

from pyssertive import AssertableValue, expect


def test_expect_should_return_assertable_value():
    assert isinstance(expect(42), AssertableValue)


def test_assertable_value_should_wrap_arbitrary_value():
    assert AssertableValue("hello")._value == "hello"


def test_equals_should_pass_when_values_are_equal():
    expect(42).equals(42)


def test_equals_should_raise_when_values_differ():
    with pytest.raises(AssertionError, match="Expected value to equal 42, got 7"):
        expect(7).equals(42)


def test_equals_should_return_self_for_chaining():
    assert expect(42).equals(42) is not None


def test_does_not_equal_should_pass_when_values_differ():
    expect(7).does_not_equal(42)


def test_does_not_equal_should_raise_when_values_are_equal():
    with pytest.raises(AssertionError, match="Expected value to not equal 42"):
        expect(42).does_not_equal(42)


def test_is_same_as_should_pass_when_identity_matches():
    sentinel = object()
    expect(sentinel).is_same_as(sentinel)


def test_is_same_as_should_raise_when_identity_differs():
    with pytest.raises(AssertionError, match="Expected value to be the same instance"):
        expect([1]).is_same_as([1])


def test_is_not_same_as_should_pass_when_identity_differs():
    expect([1]).is_not_same_as([1])


def test_is_not_same_as_should_raise_when_identity_matches():
    sentinel = object()
    with pytest.raises(AssertionError, match="Expected value to not be the same instance"):
        expect(sentinel).is_not_same_as(sentinel)


def test_is_none_should_pass_when_value_is_none():
    expect(None).is_none()


def test_is_none_should_raise_when_value_is_not_none():
    with pytest.raises(AssertionError, match="Expected value to be None, got 0"):
        expect(0).is_none()


def test_is_not_none_should_pass_when_value_is_not_none():
    expect(0).is_not_none()


def test_is_not_none_should_raise_when_value_is_none():
    with pytest.raises(AssertionError, match="Expected value to not be None"):
        expect(None).is_not_none()


@pytest.mark.parametrize("value", [1, "x", [0], {"a": 1}, True])
def test_is_truthy_should_pass_for_truthy_values(value):
    expect(value).is_truthy()


def test_is_truthy_should_raise_for_falsy_value():
    with pytest.raises(AssertionError, match="Expected value to be truthy"):
        expect(0).is_truthy()


@pytest.mark.parametrize("value", [0, "", [], {}, None, False])
def test_is_falsy_should_pass_for_falsy_values(value):
    expect(value).is_falsy()


def test_is_falsy_should_raise_for_truthy_value():
    with pytest.raises(AssertionError, match="Expected value to be falsy"):
        expect(1).is_falsy()


def test_is_true_should_pass_when_value_is_true():
    expect(True).is_true()


def test_is_true_should_raise_when_value_is_truthy_but_not_true():
    with pytest.raises(AssertionError, match="Expected value to be True, got 1"):
        expect(1).is_true()


def test_is_false_should_pass_when_value_is_false():
    expect(False).is_false()


def test_is_false_should_raise_when_value_is_falsy_but_not_false():
    with pytest.raises(AssertionError, match="Expected value to be False, got 0"):
        expect(0).is_false()


@pytest.mark.parametrize("value, cls", [("hello", str), (42, (int, str))])
def test_is_instance_of_should_pass(value, cls):
    expect(value).is_instance_of(cls)


def test_is_instance_of_should_pass_for_subclass():
    class Animal:
        pass

    class Dog(Animal):
        pass

    expect(Dog()).is_instance_of(Animal)


@pytest.mark.parametrize(
    "value, cls, pattern",
    [
        ("hello", int, "Expected value to be instance of int, got str"),
        ("hello", (int, float), r"Expected value to be instance of int \| float, got str"),
    ],
)
def test_is_instance_of_should_raise(value, cls, pattern):
    with pytest.raises(AssertionError, match=pattern):
        expect(value).is_instance_of(cls)


@pytest.mark.parametrize("cls", [int, (int, float)])
def test_is_not_instance_of_should_pass(cls):
    expect("hello").is_not_instance_of(cls)


@pytest.mark.parametrize(
    "cls, pattern",
    [
        (str, "Expected value to not be instance of str"),
        ((int, str), r"Expected value to not be instance of int \| str"),
    ],
)
def test_is_not_instance_of_should_raise(cls, pattern):
    with pytest.raises(AssertionError, match=pattern):
        expect("hello").is_not_instance_of(cls)


def test_is_type_should_pass_for_exact_type():
    expect(True).is_type(bool)


def test_is_type_should_raise_for_subclass():
    class Animal:
        pass

    class Dog(Animal):
        pass

    with pytest.raises(AssertionError, match="Expected value to be of exact type Animal, got Dog"):
        expect(Dog()).is_type(Animal)


def test_is_greater_than_should_pass_when_value_is_greater():
    expect(10).is_greater_than(5)


def test_is_greater_than_should_raise_when_value_is_equal():
    with pytest.raises(AssertionError, match="Expected value to be greater than 5, got 5"):
        expect(5).is_greater_than(5)


def test_is_less_than_should_pass_when_value_is_less():
    expect(5).is_less_than(10)


def test_is_less_than_should_raise_when_value_is_equal():
    with pytest.raises(AssertionError, match="Expected value to be less than 5, got 5"):
        expect(5).is_less_than(5)


def test_is_at_least_should_pass_when_value_is_equal():
    expect(5).is_at_least(5)


def test_is_at_least_should_pass_when_value_is_greater():
    expect(10).is_at_least(5)


def test_is_at_least_should_raise_when_value_is_less():
    with pytest.raises(AssertionError, match="Expected value to be at least 5, got 3"):
        expect(3).is_at_least(5)


def test_is_at_most_should_pass_when_value_is_equal():
    expect(5).is_at_most(5)


def test_is_at_most_should_pass_when_value_is_less():
    expect(3).is_at_most(5)


def test_is_at_most_should_raise_when_value_is_greater():
    with pytest.raises(AssertionError, match="Expected value to be at most 5, got 7"):
        expect(7).is_at_most(5)


def test_is_between_should_pass_for_value_inside_range():
    expect(5).is_between(1, 10)


def test_is_between_should_pass_for_boundary_values():
    expect(1).is_between(1, 10)
    expect(10).is_between(1, 10)


def test_is_between_should_raise_for_value_outside_range():
    with pytest.raises(AssertionError, match=r"Expected value to be between 1 and 10 \(inclusive\), got 15"):
        expect(15).is_between(1, 10)


def test_has_count_should_pass_when_length_matches():
    expect([1, 2, 3]).has_count(3)


def test_has_count_should_work_on_strings():
    expect("hello").has_count(5)


def test_has_count_should_work_on_dicts():
    expect({"a": 1, "b": 2}).has_count(2)


def test_has_count_should_raise_when_length_differs():
    with pytest.raises(AssertionError, match="Expected count of 3, got 2"):
        expect([1, 2]).has_count(3)


def test_is_empty_should_pass_for_empty_collection():
    expect([]).is_empty()
    expect("").is_empty()
    expect({}).is_empty()


def test_is_empty_should_raise_for_non_empty():
    with pytest.raises(AssertionError, match="Expected value to be empty"):
        expect([1]).is_empty()


def test_is_not_empty_should_pass_for_non_empty():
    expect([1]).is_not_empty()


def test_is_not_empty_should_raise_for_empty():
    with pytest.raises(AssertionError, match="Expected value to not be empty"):
        expect([]).is_not_empty()


def test_contains_should_pass_when_item_present():
    expect([1, 2, 3]).contains(2)


def test_contains_should_pass_when_all_items_present():
    expect([1, 2, 3]).contains(1, 3)


def test_contains_should_work_on_strings():
    expect("hello world").contains("world")


def test_contains_should_raise_when_item_absent():
    with pytest.raises(AssertionError, match="Expected value to contain 5"):
        expect([1, 2, 3]).contains(5)


def test_does_not_contain_should_pass_when_items_absent():
    expect([1, 2, 3]).does_not_contain(5, 6)


def test_does_not_contain_should_raise_when_item_present():
    with pytest.raises(AssertionError, match="Expected value to not contain 2"):
        expect([1, 2, 3]).does_not_contain(2)


def test_has_key_should_pass_when_key_present():
    expect({"a": 1, "b": 2}).has_key("a")


def test_has_key_should_raise_when_key_absent():
    with pytest.raises(AssertionError, match="Expected dict to have key 'missing'"):
        expect({"a": 1}).has_key("missing")


def test_has_key_should_raise_when_value_is_not_a_dict():
    with pytest.raises(AssertionError, match="Expected a dict, got list"):
        expect([1, 2, 3]).has_key("a")


def test_does_not_have_key_should_pass_when_key_absent():
    expect({"a": 1}).does_not_have_key("missing")


def test_does_not_have_key_should_raise_when_key_present():
    with pytest.raises(AssertionError, match="Expected dict to not have key 'a'"):
        expect({"a": 1}).does_not_have_key("a")


def test_has_keys_should_pass_when_all_keys_present():
    expect({"a": 1, "b": 2, "c": 3}).has_keys("a", "b")


def test_has_keys_should_raise_when_any_key_missing():
    with pytest.raises(AssertionError, match="Expected dict to have key 'b'"):
        expect({"a": 1}).has_keys("a", "b")


def test_has_attribute_should_pass_when_attribute_exists():
    class Obj:
        name = "alice"

    expect(Obj()).has_attribute("name")


def test_has_attribute_should_pass_when_attribute_matches_expected_value():
    class Obj:
        name = "alice"

    expect(Obj()).has_attribute("name", "alice")


def test_has_attribute_should_raise_when_attribute_missing():
    class Obj:
        pass

    with pytest.raises(AssertionError, match="Expected object to have attribute 'name'"):
        expect(Obj()).has_attribute("name")


def test_has_attribute_should_raise_when_attribute_value_mismatches():
    class Obj:
        name = "bob"

    with pytest.raises(AssertionError, match="Expected attribute 'name' to equal 'alice', got 'bob'"):
        expect(Obj()).has_attribute("name", "alice")


def test_does_not_have_attribute_should_pass_when_attribute_missing():
    class Obj:
        pass

    expect(Obj()).does_not_have_attribute("name")


def test_does_not_have_attribute_should_raise_when_attribute_present():
    class Obj:
        name = "alice"

    with pytest.raises(AssertionError, match="Expected object to not have attribute 'name'"):
        expect(Obj()).does_not_have_attribute("name")


def test_matches_should_pass_when_regex_matches():
    expect("hello world").matches(r"world")


def test_matches_should_use_search_semantics():
    expect("abc123def").matches(r"\d+")


def test_matches_should_raise_when_regex_does_not_match():
    with pytest.raises(AssertionError, match=r"Expected 'hello' to match pattern '\\d\+'"):
        expect("hello").matches(r"\d+")


def test_does_not_match_should_pass_when_regex_does_not_match():
    expect("hello").does_not_match(r"\d+")


def test_does_not_match_should_raise_when_regex_matches():
    with pytest.raises(AssertionError, match=r"Expected 'hello123' to not match pattern '\\d\+'"):
        expect("hello123").does_not_match(r"\d+")


def test_starts_with_should_pass_when_prefix_matches():
    expect("hello world").starts_with("hello")


def test_starts_with_should_raise_when_prefix_does_not_match():
    with pytest.raises(AssertionError, match="Expected 'hello' to start with 'world'"):
        expect("hello").starts_with("world")


def test_ends_with_should_pass_when_suffix_matches():
    expect("hello world").ends_with("world")


def test_ends_with_should_raise_when_suffix_does_not_match():
    with pytest.raises(AssertionError, match="Expected 'hello' to end with 'world'"):
        expect("hello").ends_with("world")


def test_each_should_apply_matcher_to_all_elements():
    expect([2, 4, 6]).each().is_greater_than(0)


def test_each_should_raise_when_any_element_fails():
    with pytest.raises(AssertionError, match="Expected value to be greater than 0, got -3"):
        expect([2, 4, -3]).each().is_greater_than(0)


def test_each_should_allow_chaining_multiple_matchers():
    expect([2, 4, 6]).each().is_instance_of(int).is_greater_than(0)


def test_each_should_raise_when_value_is_not_iterable():
    with pytest.raises(AssertionError, match="Expected an iterable, got int"):
        expect(42).each()


def test_sequence_should_pass_when_values_match_positionally():
    expect([1, 2, 3]).sequence(1, 2, 3)


def test_sequence_should_accept_predicates():
    expect([1, 2, 3]).sequence(
        lambda v: v.equals(1),
        lambda v: v.is_greater_than(1),
        lambda v: v.is_greater_than(2),
    )


def test_sequence_should_raise_when_lengths_differ():
    with pytest.raises(AssertionError, match="Expected sequence of length 3, got 2"):
        expect([1, 2]).sequence(1, 2, 3)


def test_sequence_should_raise_when_a_value_mismatches():
    with pytest.raises(AssertionError, match="Expected value to equal 99, got 3"):
        expect([1, 2, 3]).sequence(1, 2, 99)


def test_sequence_should_raise_when_value_is_not_iterable():
    with pytest.raises(AssertionError, match="Expected an iterable, got int"):
        expect(42).sequence(1, 2, 3)
