# pyssertive

[![Build Status](https://github.com/othercodes/pyssertive/actions/workflows/test.yml/badge.svg)](https://github.com/othercodes/pyssertive/actions/workflows/test.yml)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=othercodes_pyssertive&metric=coverage)](https://sonarcloud.io/summary/new_code?id=othercodes_pyssertive)

Fluent, chainable assertions for everything you test in Python. One vocabulary — from a single value to HTTP responses, JSON, HTML, MCP, and architecture. Inspired by Laravel's elegant testing API.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Expectations](#expectations)
  - [HTTP Status Assertions](#http-status-assertions)
  - [JSON Assertions](#json-assertions)
  - [JSON Schema Validation](#json-schema-validation)
  - [HTML Assertions](#html-assertions)
  - [Session and Cookie Assertions](#session-and-cookie-assertions)
  - [Template Assertions](#template-assertions)
  - [Streaming and Download Assertions](#streaming-and-download-assertions)
  - [Debug Helpers](#debug-helpers)
  - [Database Assertions](#database-assertions)
  - [Architecture Assertions](#architecture-assertions)
  - [MCP Assertions](#mcp-assertions)

## Features

- One fluent vocabulary for any value, response, or contract under test
- HTTP status code assertions (2xx, 3xx, 4xx, 5xx)
- JSON response validation with path navigation
- JSON Schema contract testing
- HTML content assertions
- Template and context assertions
- Form and formset error assertions
- Session and cookie assertions
- Header assertions
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

## Usage

### Expectations

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

#### Domain example

```python
def test_signup_should_create_active_user():
    user = signup_service.register(email="alice@x.com")

    expect(user).is_instance_of(User)
    expect(user.id).is_not_none()
    expect(user.email).equals("alice@x.com")
    expect(user.permissions).contains("read").does_not_contain("admin")
    expect(user.is_active).is_true()
```

#### Higher-order: `each` and `sequence`

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

#### Custom expectations

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

#### Unified entry point

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

#### Matchers reference

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

The sections below show how the same vocabulary specializes for HTTP, JSON,
HTML, MCP, and architectural concerns.

### HTTP Status Assertions

A complete end-to-end test wires up a `FluentHttpAssertClient` and chains assertions on the response:

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

Status-specific shortcuts:

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

| Method                                      | Purpose                                                       |
|---------------------------------------------|---------------------------------------------------------------|
| `has(key, count=None)`                      | Path exists, optionally with item count                       |
| `missing(key)`                              | Path does not exist                                           |
| `where(key, expected)`                      | Value matches (exact or callable predicate)                   |
| `where_not(key, value)`                     | Value does not equal `value` (e.g. `where_not("name", None)`) |
| `where_truthy(key)`                         | Value is truthy (not None, 0, "", [], {}, False)              |
| `where_falsy(key)`                          | Value is falsy                                                |
| `where_type(key, type)`                     | Value is an instance of `type`                                |
| `count(n)`                                  | Current scope has `n` items                                   |
| `fragment(dict)` / `missing_fragment(dict)` | Subset match / absence                                        |
| `exact(value)`                              | Full equality                                                 |
| `is_dict()` / `is_list()`                   | Type assertion                                                |
| `structure(schema)`                         | Keys + types schema validation                                |
| `json(path, callback=None)`                 | Scope into a sub-path (recursive)                             |
| `matches_schema(schema)`                    | Validate against a JSON Schema (dict, file path, or URL)      |

For ad-hoc use, `assert_json()` without a callback returns the `AssertableJson` directly:

```python
root = response.assert_json()
root.has("data").where_type("data.users", list)

scoped = response.assert_json("data.users.0")
scoped.where("name", "Alice").where_type("id", int)
```

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

| Method                                                  | Purpose                                           |
|---------------------------------------------------------|---------------------------------------------------|
| `see_html(fragment)` / `dont_see_html(fragment)`        | Raw HTML markup match (tags preserved)            |
| `see_text(text)` / `dont_see_text(text)`                | Rendered visible text match (tags stripped)       |
| `see_html_in_order([...])` / `see_text_in_order([...])` | Ordered occurrence                                |
| `count(selector, n)`                                    | Exactly `n` elements match the CSS selector       |
| `exists(selector)`                                      | At least one element matches                      |
| `missing(selector)`                                     | No elements match                                 |
| `html(selector, callback=None)`                         | Scope into the first matching element (recursive) |
| `html_contains(fragment)`                               | Django's semantic HTML comparison                 |

For ad-hoc use, `assert_html()` without a callback returns the `AssertableHtml` directly:

```python
table = response.assert_html("table#active-users")
table.count("tbody tr", 3).see_text("Alice")
```

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

> Requires the Django adapter (`pip install pyssertive[django]`).

```python
from pyssertive.adapters.django.db import (
    assert_model_exists,
    assert_model_count,
    assert_num_queries,
)

assert_model_exists(User, username="john")
assert_model_count(User, 5)

with assert_num_queries(2):
    list(User.objects.all())
```

### Architecture Assertions

Fluent assertions for the **shape** of your imports — enforce layer boundaries, bounded-context isolation, allow-lists, and forbidden dependencies as ordinary pytest tests. Powered by [`grimp`](https://github.com/seddonym/grimp).

```python
from pyssertive.arch import assert_arch

# Forbidden imports — direct or transitive
def test_shared_does_not_depend_on_bounded_contexts():
    assert_arch("shared").should_not_depend_on([
        "proxysubscription", "userprofile", "referral",
    ])

# Allow-list — `"stdlib"` is a magic token for any stdlib module
def test_domain_is_pure():
    assert_arch("shared.domain").should_only_depend_on(["stdlib", "shared.domain"])

# Required dependency — verify a contract is still in place
def test_views_use_drf():
    assert_arch("myapp.views").should_depend_on("rest_framework")
```

#### Method catalog

| Method                                                       | Purpose                                                                                                                  |
|--------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| `should_depend_on(target \| [target], directly=False)`       | Source must import target(s); transitive by default                                                                      |
| `should_not_depend_on(target \| [target], directly=False)`   | Source must not import target(s); transitive by default                                                                  |
| `should_only_depend_on(allowed \| [allowed], directly=True)` | Every dependency must match the allow-list; direct by default. `"stdlib"` expands to any `sys.stdlib_module_names` entry |
| `ignoring(patterns)`                                         | fnmatch glob patterns skipped during chain traversal — alternate non-ignored paths still flag                            |
| `module(name, callback=None)`                                | Scope into a submodule (recursive, glob supported)                                                                       |
| `assert_arch.layers([...]).should_be_independent()`          | Strict layered architecture — each layer may only depend on layers preceding it in the list                              |
| `assert_arch.modules([...]).should_be_isolated()`            | Mutual isolation across an unordered set; combine with `ignoring(...)` to allow specific bridges                         |

#### Layered architecture

```python
def test_layers_are_independent():
    assert_arch.layers([
        "myapp.domain",
        "myapp.application",
        "myapp.infrastructure",
    ]).should_be_independent()
```

Lower layers must not import higher ones. Skipping a layer downward (infra → domain directly) is allowed; only upward dependencies trigger a violation.

#### Bounded-context isolation

```python
def test_bounded_contexts_are_isolated():
    assert_arch.modules([
        "proxysubscription", "accountsuspension", "referral",
    ]).should_be_isolated().ignoring(["*.events"])
```

No module in the set may depend on any other in either direction. `ignoring(["*.events"])` grandfathers cross-talk through published event modules — alternate paths through non-ignored modules still surface.

#### Glob expansion

Glob patterns expand against the import graph and apply the assertion to every match, aggregating failures:

```python
def test_models_dont_import_views():
    assert_arch("myapp.*.models").should_not_depend_on(["myapp.*.views"])

def test_selectors_are_read_only():
    assert_arch("myapp.*.selectors").should_not_depend_on([
        "myapp.*.services", "myapp.*.use_cases",
    ])
```

A pattern that matches no module raises `ValueError` rather than passing silently.

#### Scoped callbacks

Scoped callbacks let a block of related assertions read as one expression:

```python
def test_domain_module_internals():
    assert_arch("myapp.domain", lambda d: (
        d.should_only_depend_on(["stdlib", "myapp.domain"])
         .module("events", lambda e: (
             e.should_not_depend_on("myapp.domain.aggregates")
         ))
    ))
```

The nested assertable inherits the parent's `ignoring(...)` patterns automatically.

#### Direct vs transitive

The `directly` flag flips between checking only direct imports and checking the full transitive closure. Each method has a different default that matches the natural reading of the assertion:

```python
# Transitive by default — even an indirect import counts.
assert_arch("myapp.views").should_not_depend_on("myapp.models")

# directly=True — tolerate transitive paths through services.
assert_arch("myapp.views").should_not_depend_on("myapp.models", directly=True)

# Direct by default — what the source code actually writes.
assert_arch("myapp.application").should_only_depend_on(["stdlib", "myapp.domain"])

# directly=False — strict purity; ban transitive Django leakage.
assert_arch("shared.domain").should_only_depend_on(["stdlib"], directly=False)
```

#### Error messages

Failures surface the offending import chain so you know exactly where to fix:

```
AssertionError: shared should not depend on:
  - proxysubscription: shared → shared.auth.custom_basic_authentication → proxysubscription.models
```

Typo-style mistakes raise `ValueError` with a `Did you mean ...?` hint instead of a chain check.

### MCP Assertions

The MCP module speaks **MCP, not JSON-RPC**. Tests read as the protocol does — `called the tool, it succeeded, it returned text` — never as wire-level shape checks. Works against any response object exposing `.content` and `.headers` (httpx, Django, raw `dict`), and unwraps `text/event-stream` (Streamable HTTP transport) automatically.

#### Initialize handshake

```python
from pyssertive.adapters.httpx import FluentHttpAssertClient, HttpxRequestBuilder
from pyssertive.http.mcp import MessageBuilder
from starlette.testclient import TestClient
from fastmcp import FastMCP

app = FastMCP("weather").http_app()
client = FluentHttpAssertClient(TestClient(app))

init = MessageBuilder(HttpxRequestBuilder()).initialize().build()
client.post("/mcp", content=init.content, headers=dict(init.headers))\
    .assert_ok()\
    .assert_mcp(lambda m: m
        .negotiated_protocol("2025-11-25")
        .server_named("weather")
        .supports_tools()
    )
```

#### Tool call — success

```python
call = MessageBuilder(HttpxRequestBuilder())\
    .calling_tool("get_weather", arguments={"location": "Madrid"})\
    .build()
client.post("/mcp", content=call.content, headers=dict(call.headers))\
    .assert_ok().assert_mcp(lambda m: m
        .tool("get_weather")
        .succeeds()
        .returns_text_containing("°C")
    )
```

#### Tool-level error (HTTP 200, isError=true)

```python
response.assert_mcp(lambda m: (
    m.tool("get_weather")
     .reports_tool_error()
     .with_message_containing("Invalid date")
))
```

#### Protocol error (-32601, -32602, ...)

```python
response.assert_mcp(lambda m: (
    m.tool("unknown")
     .is_rejected_as_unknown_tool()
))
```

#### Stand-alone (no HTTP wrapper)

```python
from pyssertive.protocols.mcp import AssertableMCP

AssertableMCP(payload).lists_tools()\
    .with_count(3)\
    .contains_tool("get_weather", lambda t: (
        t.documented().accepts(["location"]).accepts_optional(["units"])
    ))
```

#### Catalog-wide invariants

Apply the same assertion to every tool without enumerating names. Useful when a server rewrites its tool schema per caller (auth scopes, feature flags):

```python
AssertableMCP(payload).lists_tools().every_tool(
    lambda t: t.does_not_accept(["internal_user_id"])
)
```

#### Method catalog

The MCP module exposes five assertable types, each scoped to a different MCP structure. Navigate between them with `lists_tools()`, `tool(name)`, the `contains_tool` / `every_tool` callbacks (yielding `AssertableToolDef`), and the `content` callback (yielding `AssertableContent`).

**`AssertableMCP`** — top-level envelope (JSON-RPC response):

| Method                                                                                                                                                                                                              | Purpose                                                          |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| `negotiated_protocol(version)`                                                                                                                                                                                      | Asserts the negotiated MCP protocol version                      |
| `server_named(name)` / `server_version(version)`                                                                                                                                                                    | Asserts the server's advertised identity                         |
| `supports_tools()` / `supports_resources(*, subscribe=None)` / `supports_prompts()` / `supports_logging()`                                                                                                          | Asserts a server capability is advertised                        |
| `has_instructions()`                                                                                                                                                                                                | Asserts the `instructions` field is present                      |
| `is_rejected_as_invalid_request()` / `is_rejected_as_method_not_found()` / `is_rejected_with_invalid_params()` / `is_rejected_as_internal_error()` / `is_rejected_as_resource_not_found()` / `is_rejected_as_user_rejected()` | Asserts a specific JSON-RPC error code                           |
| `because_message_contains(substr)`                                                                                                                                                                                  | Asserts the error message contains a substring                   |
| `lists_tools()`                                                                                                                                                                                                     | Scopes into `AssertableToolList` (tools/list response)           |
| `tool(name)`                                                                                                                                                                                                        | Scopes into `AssertableToolCall` (tools/call response)           |
| `is_success()` / `has_error()` / `result()` / `error()` / `error_code()` / `error_message()`                                                                                                                        | Read-only accessors for raw envelope inspection (escape hatches) |

**`AssertableToolList`** — `tools/list` result:

| Method                              | Purpose                                                                  |
|-------------------------------------|--------------------------------------------------------------------------|
| `with_count(n)`                     | Asserts the list has exactly `n` tools                                   |
| `contains_tool(name, callback=None)`| Asserts a tool exists; optional callback for per-tool drill-in           |
| `does_not_contain_tool(name)`       | Asserts a tool is absent                                                 |
| `every_tool(callback)`              | Applies the callback to every tool in the list                           |
| `has_more_pages()`                  | Asserts the response advertises a `nextCursor`                           |

**`AssertableToolDef`** — a single tool definition (received via `contains_tool` / `every_tool` callbacks):

| Method                       | Purpose                                                       |
|------------------------------|---------------------------------------------------------------|
| `documented()`               | Asserts the tool has a non-empty description                  |
| `accepts(params)`            | Asserts each param is in `inputSchema.required`               |
| `accepts_optional(params)`   | Asserts each param is in `inputSchema.properties`             |
| `does_not_accept(params)`    | Asserts each param is NOT in `inputSchema.properties`         |
| `has_output_schema()`        | Asserts `outputSchema` is present                             |

**`AssertableToolCall`** — `tools/call` result:

| Method                                              | Purpose                                                                  |
|-----------------------------------------------------|--------------------------------------------------------------------------|
| `succeeds()`                                        | Asserts the call did not return `isError=true`                           |
| `returns_text(expected)`                            | Asserts a text content block exactly matches                             |
| `returns_text_containing(substr)`                   | Asserts a text content block contains a substring                        |
| `returns_image(*, mime_type=None)`                  | Asserts an image content block exists (optionally with mime type)        |
| `returns_content_count(n)`                          | Asserts the number of content blocks                                     |
| `returns_structured(expected)`                      | Asserts `structuredContent` equals expected                              |
| `content(index, callback)`                          | Scopes into `AssertableContent` for a specific block                     |
| `reports_tool_error()`                              | Asserts the call returned `isError=true` (tool-level error)              |
| `with_message_containing(substr)`                   | Asserts the error message contains a substring                           |
| `is_rejected_as_unknown_tool()`                     | Asserts JSON-RPC `-32601` or `-32602` with "unknown tool" message        |
| `is_rejected_with_invalid_params()`                 | Asserts JSON-RPC `-32602`                                                |

**`AssertableContent`** — a single content block (received via `content` callback):

| Method                                                                                            | Purpose                                  |
|---------------------------------------------------------------------------------------------------|------------------------------------------|
| `is_text()` / `is_image()` / `is_audio()` / `is_resource_link()` / `is_resource()`               | Asserts the block type                   |
| `text_equals(expected)`                                                                           | Asserts text block equals expected       |
| `text_contains(substr)`                                                                           | Asserts text block contains a substring  |
| `with_mime_type(expected)`                                                                        | Asserts the block's mime type            |
| `with_uri(expected)`                                                                              | Asserts the resource URI                 |

#### Building requests with `MessageBuilder`

`MessageBuilder` constructs MCP JSON-RPC messages with native MCP vocabulary on top of any transport-level `RequestBuilder`. Inject `HttpxRequestBuilder` for FastAPI/Starlette/FastMCP testing, or `DjangoRequestBuilder` for Django-hosted MCP servers — the output of `.build()` matches whichever you inject.

```python
from pyssertive.http.mcp import MessageBuilder
from pyssertive.adapters.httpx import HttpxRequestBuilder

# Handshake — returns httpx.Request
MessageBuilder(HttpxRequestBuilder()).initialize(protocol="2025-11-25").build()

# Tool call with arguments
MessageBuilder(HttpxRequestBuilder()).calling_tool("get_weather", arguments={"location": "Madrid"}).build()

# Auth / protocol / session headers chain
MessageBuilder(HttpxRequestBuilder())\
    .with_auth_token("abc123")\
    .with_protocol_version("2025-11-25")\
    .with_session_id("sess-xyz")\
    .calling_tool("ping")\
    .build()
```

**Method catalog:**

| Method                                                       | Purpose                                                                       |
|--------------------------------------------------------------|-------------------------------------------------------------------------------|
| `MessageBuilder(request_builder, path="/mcp")`               | Constructor — inject any `RequestBuilder`; `path` overrides the MCP endpoint  |
| `with_id(msg_id)`                                            | Set an explicit JSON-RPC id (default: auto-generated)                         |
| `with_auth_token(token)`                                     | Adds `Authorization: Bearer <token>` header                                   |
| `with_protocol_version(version)`                             | Adds `MCP-Protocol-Version` header                                            |
| `with_session_id(session_id)`                                | Adds `Mcp-Session-Id` header                                                  |
| `initialize(*, protocol=…, name=…, version=…)`               | `initialize` handshake                                                        |
| `listing_tools(*, cursor=None)`                              | `tools/list`                                                                  |
| `calling_tool(name, *, arguments=None)`                      | `tools/call`                                                                  |
| `listing_resources(*, cursor=None)`                          | `resources/list`                                                              |
| `reading_resource(uri)`                                      | `resources/read`                                                              |
| `listing_prompts(*, cursor=None)`                            | `prompts/list`                                                                |
| `getting_prompt(name, *, arguments=None)`                    | `prompts/get`                                                                 |
| `notifying(method, *, params=None)`                          | `notifications/*` — fire-and-forget message (no `id` field)                   |
| `calling(method)` / `with_params(params)`                    | Low-level escape hatch for arbitrary JSON-RPC methods                         |
| `build()`                                                    | Returns the request object (`httpx.Request`, `HttpRequest`, etc.)             |

Pair it naturally with `assert_mcp` for symmetric request/response code:

```python
import httpx

client = httpx.Client(base_url="http://testserver", transport=...)
request = MessageBuilder(HttpxRequestBuilder()).calling_tool("get_weather").build()
response = client.send(request)

# Or send via the builder directly
response = MessageBuilder(HttpxRequestBuilder()).calling_tool("get_weather").build()
```

#### Builder layers

Builders form a transport-agnostic stack:

```
pyssertive.http.request.RequestBuilder    (agnostic base — method/path/headers/body/query/cookies)
  ├── pyssertive.adapters.django.DjangoRequestBuilder    → produces HttpRequest (RequestFactory)
  └── pyssertive.adapters.httpx.HttpxRequestBuilder       → produces httpx.Request (.send() also dispatches)

pyssertive.http.mcp.MessageBuilder         (composes any RequestBuilder — adds MCP JSON-RPC layer)
```

Each layer speaks its dominio: the base builder knows HTTP transport, the adapter subclasses know their framework, the MCP message builder knows JSON-RPC. New frameworks (Flask, requests, …) only require a new `RequestBuilder` subclass — MCP comes along for free.

Content-block scoping for richer tool responses:

```python
response.assert_mcp(lambda m: m.tool("render")
    .succeeds()
    .content(0, lambda c: c.is_text().text_equals("ok"))
    .content(1, lambda c: c.is_image().with_mime_type("image/png").with_base64_data())
)
```
