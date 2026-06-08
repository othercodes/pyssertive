# Expectations

Pyssertive's foundation is a single fluent vocabulary that speaks to any value
you put under test — a domain object, a primitive, a collection. Every other
assertable in this library (HTTP responses, JSON, HTML, MCP, architecture)
extends this same idiom.

```python
from pyssertive import expect

expect(42).equals(42)
expect("alice@example.com").is_instance_of(str).matches(r".+@.+")
expect([1, 2, 3]).has_count(3).contains(2).does_not_contain(99)
expect({"name": "alice", "age": 30}).has_keys("name", "age")
```

## Domain example

```python
def test_signup_should_create_active_user():
    user = signup_service.register(email="alice@x.com")

    expect(user).is_instance_of(User)
    expect(user.id).is_not_none()
    expect(user.email).equals("alice@x.com")
    expect(user.permissions).contains("read").does_not_contain("admin")
    expect(user.is_active).is_true()
```

## Higher-order: `each` and `sequence`

Apply matchers to every element of an iterable, or match positionally with
optional predicates:

```python
expect([2, 4, 6]).each().is_greater_than(0).is_instance_of(int)

expect(orders).sequence(
    lambda o: o.has_attribute("status", "paid"),
    lambda o: o.has_attribute("status", "shipped"),
    lambda o: o.has_attribute("status", "delivered"),
)
```

## Custom expectations

Subclass `AssertableValue` to add domain-specific matchers — fully typed,
autocompleted by your IDE, checked by mypy:

```python
from pyssertive import AssertableValue

class UserExpectation(AssertableValue):
    def is_admin(self):
        assert "admin" in self._value.permissions, "Expected user to be admin"
        return self

    def is_verified(self):
        assert self._value.verified_at is not None, "Expected user to be verified"
        return self

def expect_user(u): return UserExpectation(u)

expect_user(user).is_admin().is_verified().has_attribute("email")
```

## Unified entry point

`expect` is also a dispatcher to the specialized assertables, same fluent style for any subject:

```python
from pyssertive import expect

expect(user)                # → AssertableValue (generic)
expect.json(payload)        # → AssertableJson (dict / str / bytes)
expect.html(markup)         # → AssertableHtml (str / bytes)
expect.mcp(envelope)        # → AssertableMCP (dict / response)
expect.arch("myapp.domain") # → AssertableArch (module name)
```

Each factory uses lazy imports — `from pyssertive import expect` stays light and only loads the specialized modules on first use. The direct constructors (`AssertableJson(...)`, `AssertableHtml(...)`, `assert_arch(...)`, etc.) remain available for code that prefers them.

## Matchers reference

| Category     | Matchers                                                                                       |
| ------------ | ---------------------------------------------------------------------------------------------- |
| Equality     | `equals`, `does_not_equal`, `is_same_as`, `is_not_same_as`, `is_none`, `is_not_none`           |
| Truthiness   | `is_truthy`, `is_falsy`, `is_true`, `is_false`                                                 |
| Types        | `is_instance_of`, `is_not_instance_of`, `is_type`                                              |
| Comparison   | `is_greater_than`, `is_less_than`, `is_at_least`, `is_at_most`, `is_between`                   |
| Collections  | `has_count`, `is_empty`, `is_not_empty`, `contains`, `does_not_contain`                        |
| Dict/object  | `has_key`, `does_not_have_key`, `has_keys`, `has_attribute`, `does_not_have_attribute`         |
| Strings      | `matches`, `does_not_match`, `starts_with`, `ends_with`                                        |
| Higher-order | `each`, `sequence`                                                                             |

The other guides show how the same vocabulary specializes for HTTP, JSON,
HTML, MCP, and architectural concerns.
