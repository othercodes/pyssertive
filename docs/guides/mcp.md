# MCP Assertions

The MCP module speaks **MCP, not JSON-RPC**. Tests read as the protocol does — `called the tool, it succeeded, it returned text` — never as wire-level shape checks. Works against any response object exposing `.content` and `.headers` (httpx, Django, raw `dict`), and unwraps `text/event-stream` (Streamable HTTP transport) automatically.

## Initialize handshake

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

## Tool call — success

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

## Tool-level error (HTTP 200, isError=true)

```python
response.assert_mcp(lambda m: (
    m.tool("get_weather")
     .reports_tool_error()
     .with_message_containing("Invalid date")
))
```

## Protocol error (-32601, -32602, ...)

```python
response.assert_mcp(lambda m: (
    m.tool("unknown")
     .is_rejected_as_unknown_tool()
))
```

## Stand-alone (no HTTP wrapper)

```python
from pyssertive.protocols.mcp import AssertableMCP

AssertableMCP(payload).lists_tools()\
    .with_count(3)\
    .contains_tool("get_weather", lambda t: (
        t.documented().accepts(["location"]).accepts_optional(["units"])
    ))
```

## Catalog-wide invariants

Apply the same assertion to every tool without enumerating names. Useful when a server rewrites its tool schema per caller (auth scopes, feature flags):

```python
AssertableMCP(payload).lists_tools().every_tool(
    lambda t: t.does_not_accept(["internal_user_id"])
)
```

## Prompts — `prompts/list` and `prompts/get`

```python
# Catalog discovery
AssertableMCP(payload).lists_prompts()\
    .with_count(2)\
    .contains_prompt("code_review", lambda p: (
        p.documented().accepts(["code"]).accepts_optional(["language"])
    ))

# Rendered messages
AssertableMCP(payload).prompt("code_review")\
    .succeeds()\
    .with_message_count(1)\
    .first_message().is_from_user().content().is_not_empty()

# Multi-modal message content (dual-mode chain through content())
AssertableMCP(payload).prompt("review")\
    .first_message().content().with_mime_type("image/png").with_base64_data()

# Or via callback (parent chain continues)
AssertableMCP(payload).prompt("review")\
    .first_message(lambda m: m.content(lambda c: c.with_text_containing("review")))\
    .with_message_count(1)

# Server rejected the get with invalid params
AssertableMCP(payload).prompt("review")\
    .is_rejected_with_invalid_params()\
    .with_message_containing("missing required argument")
```

## Method catalog

The MCP module is navigable from `AssertableMCP` (envelope) → list classes (`AssertableToolList`, `AssertablePromptList`) → per-invocation classes (`AssertableToolCall`, `AssertablePromptGet`) → per-item classes (`AssertableToolDef`, `AssertablePromptDef`, `AssertablePromptMessage`) → `AssertableContent` for individual content blocks. `AssertableContent` carries all type-aware assertions in one class: methods like `with_text` / `with_mime_type` / `with_uri` validate the block type implicitly before checking the value (auto-dispatching across compatible types where the wire format differs, e.g. text vs embedded resource text). Drill-in methods (`content(...)`, `first_message(...)`, etc.) are **dual-mode**: called without a callback they return the child for direct chaining; called with a callback they invoke it and return Self for parent-chain continuation — same pattern as `assert_json` / `assert_html`.

**`AssertableMCP`** — top-level envelope (JSON-RPC response):

| Method                                                                                                                                                                                                              | Purpose                                                          |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| `negotiated_protocol(version)`                                                                                                                                                                                      | Asserts the negotiated MCP protocol version                      |
| `server_named(name)` / `server_version(version)`                                                                                                                                                                    | Asserts the server's advertised identity                         |
| `supports_tools()` / `supports_resources(*, subscribe=None)` / `supports_prompts()` / `supports_logging()`                                                                                                          | Asserts a server capability is advertised                        |
| `has_instructions()`                                                                                                                                                                                                | Asserts the `instructions` field is present                      |
| `is_rejected_as_invalid_request()` / `is_rejected_as_method_not_found()` / `is_rejected_with_invalid_params()` / `is_rejected_as_internal_error()` / `is_rejected_as_resource_not_found()` / `is_rejected_as_user_rejected()` | Asserts a specific JSON-RPC error code                           |
| `is_rejected_with_code(code)`                                                                                                                                                                                       | Asserts an arbitrary JSON-RPC error code (e.g. application-level `-32001`) |
| `because_message_contains(substr)` / `because_message_equals(expected)`                                                                                                                                             | Asserts the error message contains a substring or matches exactly |
| `lists_tools()`                                                                                                                                                                                                     | Scopes into `AssertableToolList` (tools/list response)           |
| `tool(name)`                                                                                                                                                                                                        | Scopes into `AssertableToolCall` (tools/call response)           |
| `lists_prompts()`                                                                                                                                                                                                   | Scopes into `AssertablePromptList` (prompts/list response)       |
| `prompt(name)`                                                                                                                                                                                                      | Scopes into `AssertablePromptGet` (prompts/get response)         |
| `is_prompts_list_changed_notification()`                                                                                                                                                                            | Asserts envelope is the `notifications/prompts/list_changed` notification |
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
| `returns_structured(expected)`                      | Asserts `structuredContent` equals expected                             |
| `content(index, callback=None)`                     | Dual-mode: scopes into `AssertableContent`; with callback returns Self   |
| `reports_tool_error()`                              | Asserts the call returned `isError=true` (tool-level error)              |
| `with_message_containing(substr)`                   | Asserts the error message contains a substring                           |
| `is_rejected_as_unknown_tool()`                     | Asserts JSON-RPC `-32601` or `-32602` with "unknown tool" message        |
| `is_rejected_with_invalid_params()`                 | Asserts JSON-RPC `-32602`                                                |

**`AssertableContent`** — a single content block (received via `content(...)` callback or chain). All value assertions check the block type implicitly; `with_text` / `with_mime_type` / `with_uri` auto-dispatch across compatible types (e.g. `with_uri` works on both `resource_link` and embedded `resource`):

| Method                            | Compatible types                                  | Purpose                                                       |
|-----------------------------------|---------------------------------------------------|---------------------------------------------------------------|
| `is_text()` / `is_image()` / `is_audio()` / `is_resource_link()` / `is_resource()` | — | Standalone type guard (just validates the block type, returns Self) |
| `with_text(expected)`             | text, resource                                    | Asserts the text payload exactly matches                      |
| `with_text_containing(substr)`    | text, resource                                    | Asserts the text payload contains a substring                 |
| `is_not_empty()`                  | text, resource, image, audio                      | Asserts the block carries a payload (text, embedded text/blob, or binary data) |
| `with_mime_type(expected)`        | image, audio, resource_link, resource             | Asserts the block's mime type                                 |
| `with_base64_data()`              | image, audio                                      | Asserts `data` is a non-empty valid base64 string             |
| `with_blob_data()`                | resource                                          | Asserts the embedded `blob` is a non-empty valid base64 string |
| `with_uri(expected)`              | resource_link, resource                           | Asserts the URI (auto-dispatches between top-level `uri` and embedded `resource.uri`) |
| `named(expected)`                 | resource_link, resource                           | Asserts the `name` field (auto-dispatches between top-level and embedded) |

**`AssertablePromptList`** — `prompts/list` result:

| Method                                | Purpose                                                                  |
|---------------------------------------|--------------------------------------------------------------------------|
| `with_count(n)`                       | Asserts the list has exactly `n` prompts                                 |
| `contains_prompt(name, callback=None)`| Asserts a prompt exists; optional callback for per-prompt drill-in       |
| `does_not_contain_prompt(name)`       | Asserts a prompt is absent                                               |
| `every_prompt(callback)`              | Applies the callback to every prompt in the list                         |
| `has_more_pages()`                    | Asserts the response advertises a `nextCursor`                           |

**`AssertablePromptDef`** — a single prompt definition (received via `contains_prompt` / `every_prompt` callbacks):

| Method                       | Purpose                                                       |
|------------------------------|---------------------------------------------------------------|
| `documented()`               | Asserts the prompt has a non-empty description                |
| `accepts(args)`              | Asserts each arg is declared with `required: true`            |
| `accepts_optional(args)`     | Asserts each arg is declared without `required: true`         |
| `does_not_accept(args)`      | Asserts each arg is NOT in the `arguments` array              |

**`AssertablePromptGet`** — `prompts/get` result:

| Method                                         | Purpose                                                                  |
|------------------------------------------------|--------------------------------------------------------------------------|
| `succeeds()`                                   | Asserts the response is a valid `prompts/get` result (no protocol error) |
| `with_description(expected)`                   | Asserts the `description` field exactly matches                          |
| `with_description_containing(substr)`          | Asserts the `description` contains a substring                           |
| `with_message_count(n)`                        | Asserts the messages list has exactly `n` items                          |
| `first_message(callback=None)`                 | Dual-mode: scopes into `AssertablePromptMessage` at index 0              |
| `message(index, callback=None)`                | Dual-mode: scopes into `AssertablePromptMessage` at the given index      |
| `last_message(callback=None)`                  | Dual-mode: scopes into `AssertablePromptMessage` at the last index       |
| `every_message(callback)`                      | Applies the callback to every message                                    |
| `is_rejected_with_invalid_params()`            | Asserts JSON-RPC `-32602` (used when the server rejects bad arguments)   |
| `with_message_containing(substr)`              | Asserts the protocol error message contains a substring                  |

**`AssertablePromptMessage`** — a single message inside a `prompts/get` response:

| Method                                | Purpose                                                                  |
|---------------------------------------|--------------------------------------------------------------------------|
| `is_from_user()` / `is_from_assistant()` | Asserts the message role                                              |
| `content(callback=None)`              | Dual-mode: scopes into `AssertableContent` (single content per message)  |

## Building requests with `MessageBuilder`

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

## Builder layers

Builders form a transport-agnostic stack:

```
pyssertive.http.request.RequestBuilder    (agnostic base — method/path/headers/body/query/cookies)
  ├── pyssertive.adapters.django.DjangoRequestBuilder    → produces HttpRequest (RequestFactory)
  └── pyssertive.adapters.httpx.HttpxRequestBuilder       → produces httpx.Request (.send() also dispatches)

pyssertive.http.mcp.MessageBuilder         (composes any RequestBuilder — adds MCP JSON-RPC layer)
```

Each layer speaks its domain: the base builder knows HTTP transport, the adapter subclasses know their framework, the MCP message builder knows JSON-RPC. New frameworks (Flask, requests, …) only require a new `RequestBuilder` subclass — MCP comes along for free.

Content-block scoping for richer tool responses:

```python
response.assert_mcp(lambda m: m.tool("render")
    .succeeds()
    .content(0, lambda c: c.is_text().with_text("ok"))
    .content(1, lambda c: c.is_image().with_mime_type("image/png").with_base64_data())
)
```
