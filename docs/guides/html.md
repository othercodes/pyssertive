# HTML Assertions

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

## Scoped HTML assertions with `assert_html`

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
