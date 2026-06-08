# pyssertive

[![Build Status](https://github.com/othercodes/pyssertive/actions/workflows/test.yml/badge.svg)](https://github.com/othercodes/pyssertive/actions/workflows/test.yml)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=othercodes_pyssertive&metric=coverage)](https://sonarcloud.io/summary/new_code?id=othercodes_pyssertive)

Fluent, chainable assertions for everything you test in Python. One vocabulary —
from a single value to HTTP responses, JSON, HTML, MCP, and architecture. Inspired
by Laravel's elegant testing API.

```python
from pyssertive import expect

expect(user).is_instance_of(User)
expect.json(payload).where("status", "active").missing("password")
expect.arch("myapp.domain").should_only_depend_on(["stdlib", "myapp.domain"])
```

## Why pyssertive

Every assertable in this library extends a single fluent idiom. Learn the
vocabulary once — `equals`, `contains`, `has_key`, `where`, `each`, `sequence` —
and it specializes consistently for HTTP responses, JSON payloads, HTML markup,
MCP envelopes, and your import graph.

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

## Get started

- [Installation](getting-started/installation.md) — install the core package and optional adapters.
- [Quickstart](getting-started/quickstart.md) — your first assertions in a few lines.
- [Guides](guides/expectations.md) — task-focused walkthroughs for every assertable.
- [API Reference](api/index.md) — the full class and method surface.
