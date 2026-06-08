# HTTP Responses

All HTTP assertions hang off a `FluentResponse` returned by a
`FluentHttpAssertClient`. The same fluent vocabulary covers status codes,
sessions, cookies, templates, streaming bodies, and debug output.

## Status assertions

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

JSON and HTML assertions on the response are covered in their own guides:
[JSON](json.md) and [HTML](html.md).

## Session and cookie assertions

```python
response.assert_session_has("user_id", 123)\
    .assert_session_missing("temp_token")\
    .assert_cookie("session_id")\
    .assert_cookie_missing("tracking")
```

## Template assertions

```python
response.assert_template_used("users/list.html")\
    .assert_context_has("users")\
    .assert_context_equals("page", 1)
```

## Streaming and download assertions

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

## Debug helpers

```python
response.dump()           # Print full response
response.dump_json()      # Pretty print JSON
response.dump_headers()   # Print headers
response.dump_session()   # Print session data
response.dd()             # Dump and die (raises exception)
```
