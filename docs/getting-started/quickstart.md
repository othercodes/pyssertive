# Quickstart

Pyssertive's foundation is a single fluent vocabulary that speaks to any value you
put under test. Start with plain values:

```python
from pyssertive import expect

expect(42).equals(42)
expect("alice@example.com").is_instance_of(str).matches(r".+@.+")
expect([1, 2, 3]).has_count(3).contains(2).does_not_contain(99)
expect({"name": "alice", "age": 30}).has_keys("name", "age")
```

The same `expect` is a dispatcher into the specialized assertables:

```python
expect(user)                # → AssertableValue (generic)
expect.json(payload)        # → AssertableJson (dict / str / bytes)
expect.html(markup)         # → AssertableHtml (str / bytes)
expect.mcp(envelope)        # → AssertableMCP (dict / response)
expect.arch("myapp.domain") # → AssertableArch (module name)
```

A complete end-to-end HTTP test wires up a client and chains assertions on the
response:

```python
import pytest
from pyssertive.adapters.django import FluentHttpAssertClient


@pytest.fixture
def client():
    from django.test import Client
    return FluentHttpAssertClient(Client())


@pytest.mark.django_db
def test_user_api(client):
    response = client.get("/api/users/")

    response.assert_ok()\
        .assert_json_path("count", 10)\
        .assert_header("Content-Type", "application/json")
```

From here, dive into the guides:

- [Expectations](../guides/expectations.md) — the core vocabulary and custom matchers.
- [HTTP responses](../guides/http.md) — status, sessions, templates, streaming, debug.
- [JSON](../guides/json.md) · [HTML](../guides/html.md) · [Database](../guides/database.md) · [Architecture](../guides/architecture.md) · [MCP](../guides/mcp.md).
