# pyssertive

[![Build Status](https://github.com/othercodes/pyssertive/actions/workflows/test.yml/badge.svg)](https://github.com/othercodes/pyssertive/actions/workflows/test.yml)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=othercodes_pyssertive&metric=coverage)](https://sonarcloud.io/summary/new_code?id=othercodes_pyssertive)

Fluent, chainable assertions for everything you test in Python. One vocabulary —
from a single value to HTTP responses, JSON, HTML, MCP, and architecture. Inspired
by Laravel's elegant testing API.

## 📚 Documentation

**Full documentation lives at [othercodes.github.io/pyssertive](https://othercodes.github.io/pyssertive/).**

- [Installation](https://othercodes.github.io/pyssertive/getting-started/installation/)
- [Quickstart](https://othercodes.github.io/pyssertive/getting-started/quickstart/)
- Guides: [Expectations](https://othercodes.github.io/pyssertive/guides/expectations/) ·
  [HTTP](https://othercodes.github.io/pyssertive/guides/http/) ·
  [JSON](https://othercodes.github.io/pyssertive/guides/json/) ·
  [HTML](https://othercodes.github.io/pyssertive/guides/html/) ·
  [Database](https://othercodes.github.io/pyssertive/guides/database/) ·
  [Architecture](https://othercodes.github.io/pyssertive/guides/architecture/) ·
  [MCP](https://othercodes.github.io/pyssertive/guides/mcp/)
- [API Reference](https://othercodes.github.io/pyssertive/api/)

## Features

- One fluent vocabulary for any value, response, or contract under test
- HTTP status code assertions (2xx, 3xx, 4xx, 5xx)
- JSON response validation with path navigation, fragments, and JSON Schema contract testing
- HTML content assertions with CSS-selector scoping
- Template, context, session, cookie, and header assertions
- Streaming response and file download assertions
- Architecture assertions for import boundaries, layers, and bounded-context isolation
- MCP (Model Context Protocol) assertions with MCP-native vocabulary
- Debug helpers for test development

## Requirements

- Python 3.10+
- Django 4.2, 5.2, or 6.0 (optional, only if using the Django adapter)
- httpx 0.27+ (optional, only if using the httpx adapter for FastAPI/Starlette/FastMCP)

## Installation

```bash
pip install pyssertive            # core
pip install pyssertive[django]    # with Django adapter
pip install pyssertive[httpx]     # with httpx adapter (FastAPI, Starlette, FastMCP)
```

## Quickstart

```python
from pyssertive import expect

# Generic values — one vocabulary for anything
expect(42).equals(42)
expect([1, 2, 3]).has_count(3).contains(2).does_not_contain(99)
expect("alice@example.com").is_instance_of(str).matches(r".+@.+")

# The same expect dispatches to specialized assertables
expect.json(payload).where("status", "active").missing("password")
expect.html(markup).see_text("Welcome back, Alice")
expect.arch("myapp.domain").should_only_depend_on(["stdlib", "myapp.domain"])
```

HTTP responses chain fluently from a test client:

```python
import pytest
from pyssertive.adapters.django import FluentHttpAssertClient


@pytest.fixture
def client():
    from django.test import Client
    return FluentHttpAssertClient(Client())


@pytest.mark.django_db
def test_user_api(client):
    client.get("/api/users/")\
        .assert_ok()\
        .assert_json_path("count", 10)\
        .assert_header("Content-Type", "application/json")
```

See the [documentation](https://othercodes.github.io/pyssertive/) for the full guides and API reference.

## License

MIT — see [LICENSE](LICENSE).
