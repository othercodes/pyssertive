# JSON Assertions

```python
response.assert_ok()\
    .assert_json_path("user.name", "John")\
    .assert_json_fragment({"status": "active"})\
    .assert_json_count(5, path="items")\
    .assert_json_structure({"id": int, "name": str})\
    .assert_json_is_list()
```

## Scoped JSON assertions with `assert_json`

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

## JSON Schema Validation

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

### Schema from a local file

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

### Schema from a URL

```python
response.assert_json_schema("https://api.example.com/schemas/user.json")
```

### Chaining with other assertions

`assert_json_schema` returns `Self`, so it chains naturally with every other assertion:

```python
client.get("/api/users/1/")\
    .assert_ok()\
    .assert_json_schema(SCHEMAS / "user.json")\
    .assert_json_path("name", "Alice")\
    .assert_header("Content-Type", "application/json")
```

### Scoped schema validation

Because `matches_schema` lives on `AssertableJson`, it works inside scoped callbacks too — validate a nested fragment against its own schema:

```python
user_schema = {"type": "object", "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}, "required": ["id", "name"]}

response.assert_json("data.user", lambda user: (
    user.matches_schema(user_schema)
))
```

### Error messages

When validation fails, the error message includes the exact path and reason:

```
AssertionError: JSON schema validation failed at 'email': 'not-an-email' is not a 'email'
```
