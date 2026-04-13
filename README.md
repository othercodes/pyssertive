# pyssertive

[![Build Status](https://github.com/othercodes/pyssertive/actions/workflows/test.yml/badge.svg)](https://github.com/othercodes/pyssertive/actions/workflows/test.yml)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=othercodes_pyssertive&metric=coverage)](https://sonarcloud.io/summary/new_code?id=othercodes_pyssertive)

Fluent, chainable assertions for Django tests. Inspired by Laravel's elegant testing API.

## Features

- Fluent, chainable API for readable test assertions
- HTTP status code assertions (2xx, 3xx, 4xx, 5xx)
- JSON response validation with path navigation
- JSON Schema contract testing
- HTML content assertions
- Template and context assertions
- Form and formset error assertions
- Session and cookie assertions
- Header assertions
- Streaming response and file download assertions
- Debug helpers for test development

## Requirements

- Python 3.10+
- Django 4.2, 5.2, or 6.0

## Installation

```bash
pip install pyssertive
```

## Usage

### Basic Example

```python
import pytest
from pyssertive.http import FluentHttpAssertClient

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

### HTTP Status Assertions

```python
response.assert_ok()              # 2xx
response.assert_created()         # 201
response.assert_not_found()       # 404
response.assert_forbidden()       # 403
response.assert_redirect("/login/")
response.assert_status(418)       # Any status code
```

### JSON Assertions

```python
response.assert_ok()\
    .assert_json_path("user.name", "John")\
    .assert_json_fragment({"status": "active"})\
    .assert_json_count(5, path="items")\
    .assert_json_structure({"id": int, "name": str})\
    .assert_json_is_list()
```

#### Scoped JSON assertions with `assert_json`

Scope assertions to a nested path in the JSON response. The closure receives an `AssertableJson` bound to the resolved sub-tree; after it returns, the outer chain continues at the response level.

```python
response.assert_ok().assert_json("data.user", lambda user: (
    user
    .where("id", 1)
    .where_type("email", str)
    .where("age", lambda v: v >= 18)   # predicate
    .missing("password")
    .has("profile")
    .json("profile", lambda p: p.where("verified", True))  # nesting
)).assert_json_path("meta.version", "1.0")
```

Inside an `AssertableJson` scope the `assert_` prefix is dropped for brevity. Available methods:

| Method | Purpose |
|---|---|
| `has(key, count=None)` | Path exists, optionally with item count |
| `missing(key)` | Path does not exist |
| `where(key, expected)` | Value matches (exact or callable predicate) |
| `where_not(key, value)` | Value does not equal `value` (e.g. `where_not("name", None)`) |
| `where_truthy(key)` | Value is truthy (not None, 0, "", [], {}, False) |
| `where_falsy(key)` | Value is falsy |
| `where_type(key, type)` | Value is an instance of `type` |
| `count(n)` | Current scope has `n` items |
| `fragment(dict)` / `missing_fragment(dict)` | Subset match / absence |
| `exact(value)` | Full equality |
| `is_dict()` / `is_list()` | Type assertion |
| `structure(schema)` | Keys + types schema validation |
| `json(path, callback=None)` | Scope into a sub-path (recursive) |
| `matches_schema(schema)` | Validate against a JSON Schema (dict, file path, or URL) |

For ad-hoc use, `assert_json()` without a callback returns the `AssertableJson` directly:

```python
root = response.assert_json()
root.has("data").where_type("data.users", list)

scoped = response.assert_json("data.users.0")
scoped.where("name", "Alice").where_type("id", int)
```

> **Breaking change:** `assert_json()` now returns an `AssertableJson` instead of `Self`. Code that chains `.assert_json()` in the middle of a response chain (e.g. `response.assert_json().assert_json_path(...)`) should drop the `.assert_json()` call — it was always redundant since each `assert_json_*` method validates internally.

> **Deprecation note:** `assert_json_is_object` and `assert_json_is_array` are deprecated in favor of `assert_json_is_dict` and `assert_json_is_list`. They still work and emit a `DeprecationWarning`.

### JSON Schema Validation

Validate entire JSON responses against a [JSON Schema](https://json-schema.org/) for contract testing. Accepts inline dicts, local files, or remote URLs.

```python
# Inline schema
response.assert_ok().assert_json_schema({
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
    },
    "required": ["id", "name", "email"],
})
```

#### Schema from a local file

Keep your schemas alongside your tests or in a shared `schemas/` directory:

```python
from pathlib import Path

SCHEMAS = Path(__file__).parent / "schemas"

def test_user_api(client):
    client.get("/api/users/1/").assert_ok().assert_json_schema(SCHEMAS / "user.json")
```

A plain string path works too:

```python
response.assert_json_schema("tests/schemas/user.json")
```

#### Schema from a URL

```python
response.assert_json_schema("https://api.example.com/schemas/user.json")
```

#### Chaining with other assertions

`assert_json_schema` returns `Self`, so it chains naturally with every other assertion:

```python
client.get("/api/users/1/")\
    .assert_ok()\
    .assert_json_schema(SCHEMAS / "user.json")\
    .assert_json_path("name", "Alice")\
    .assert_header("Content-Type", "application/json")
```

#### Scoped schema validation

Because `matches_schema` lives on `AssertableJson`, it works inside scoped callbacks too — validate a nested fragment against its own schema:

```python
user_schema = {"type": "object", "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}, "required": ["id", "name"]}

response.assert_json("data.user", lambda user: (
    user.matches_schema(user_schema)
))
```

#### Error messages

When validation fails, the error message includes the exact path and reason:

```
AssertionError: JSON schema validation failed at 'email': 'not-an-email' is not a 'email'
```

### HTML Assertions

Two explicit families of content assertions:

- `assert_see_html` / `assert_dont_see_html` — operate on the raw HTML markup (tags preserved). Use when asserting tag structure, class names, attribute values, or specific HTML fragments.
- `assert_see_text` / `assert_dont_see_text` — operate on the rendered visible text (tags stripped). Use when asserting what a reader would see.

```python
response.assert_see_html("<strong>Welcome</strong>")\
    .assert_see_text("Welcome back, Alice")\
    .assert_dont_see_text("Error")\
    .assert_see_html_in_order(["<nav>", "<main>", "<footer>"])\
    .assert_see_text_in_order(["Dashboard", "Reports", "Settings"])\
    .assert_html_contains("<h1>Dashboard</h1>")
```

#### Scoped HTML assertions with `assert_html`

Scope assertions to a specific section of the response via CSS selectors. The closure receives an `AssertableHtml` bound to the matched sub-tree; after it returns, the outer chain continues at the document level.

```python
response.assert_ok()\
    .assert_see_text("Dashboard")\
    .assert_html("table#active-users", lambda users: (
        users
        .count("tbody tr", 3)
        .see_text("Alice")
        .dont_see_text("banned@example.com")
        .html("tr:first-child", lambda row: row.see_text("Alice"))  # nesting
    ))\
    .assert_html("section#billing", lambda s: s.see_text("alice@example.com"))\
    .assert_html("section#audit-log", lambda s: s.dont_see_text("alice@example.com"))\
    .assert_see_text("Footer text outside the table")
```

Inside an `AssertableHtml` scope the `assert_` prefix is dropped for brevity. Available methods:

| Method | Purpose |
|---|---|
| `see_html(fragment)` / `dont_see_html(fragment)` | Raw HTML markup match (tags preserved) |
| `see_text(text)` / `dont_see_text(text)` | Rendered visible text match (tags stripped) |
| `see_html_in_order([...])` / `see_text_in_order([...])` | Ordered occurrence |
| `count(selector, n)` | Exactly `n` elements match the CSS selector |
| `exists(selector)` | At least one element matches |
| `missing(selector)` | No elements match |
| `html(selector, callback=None)` | Scope into the first matching element (recursive) |
| `html_contains(fragment)` | Django's semantic HTML comparison |

For ad-hoc use, `assert_html()` without a callback returns the `AssertableHtml` directly:

```python
table = response.assert_html("table#active-users")
table.count("tbody tr", 3).see_text("Alice")
```

> **Deprecation note:** `assert_see`, `assert_dont_see`, and `assert_see_in_order` are deprecated in favor of the explicit `_html` / `_text` pairs. They still work and emit a `DeprecationWarning` pointing at both replacements.

### Session and Cookie Assertions

```python
response.assert_session_has("user_id", 123)\
    .assert_session_missing("temp_token")\
    .assert_cookie("session_id")\
    .assert_cookie_missing("tracking")
```

### Template Assertions

```python
response.assert_template_used("users/list.html")\
    .assert_context_has("users")\
    .assert_context_equals("page", 1)
```

### Streaming and Download Assertions

```python
response.assert_streaming()\
    .assert_download("report.csv")\
    .assert_streaming_contains("Expected content")\
    .assert_streaming_not_contains("Sensitive data")\
    .assert_streaming_matches(r"ID:\d+")\
    .assert_streaming_line_count(exact=10)\
    .assert_streaming_line_count(min=5, max=20)\
    .assert_streaming_csv_header(["id", "name", "email"])\
    .assert_streaming_line(0, "header,row")\
    .assert_streaming_empty()
```

### Debug Helpers

```python
response.dump()           # Print full response
response.dump_json()      # Pretty print JSON
response.dump_headers()   # Print headers
response.dump_session()   # Print session data
response.dd()             # Dump and die (raises exception)
```

### Database Assertions

```python
from pyssertive.db import (
    assert_model_exists,
    assert_model_count,
    assert_num_queries,
)

assert_model_exists(User, username="john")
assert_model_count(User, 5)

with assert_num_queries(2):
    list(User.objects.all())
```
