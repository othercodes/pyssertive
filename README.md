# pyssertive

[![Build Status](https://github.com/othercodes/pyssertive/actions/workflows/test.yml/badge.svg)](https://github.com/othercodes/pyssertive/actions/workflows/test.yml)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=othercodes_pyssertive&metric=coverage)](https://sonarcloud.io/summary/new_code?id=othercodes_pyssertive)

Fluent, chainable assertions for Django tests. Inspired by Laravel's elegant testing API.

## Features

- Fluent, chainable API for readable test assertions
- HTTP status code assertions (2xx, 3xx, 4xx, 5xx)
- JSON response validation with path navigation
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
        .assert_json()\
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
response.assert_json()\
    .assert_json_path("user.name", "John")\
    .assert_json_fragment({"status": "active"})\
    .assert_json_count(5, path="items")\
    .assert_json_structure({"id": int, "name": str})\
    .assert_json_is_array()
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
