# Architecture Assertions

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

## Method catalog

| Method                                                       | Purpose                                                                                                                  |
|--------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| `should_depend_on(target \| [target], directly=False)`       | Source must import target(s); transitive by default                                                                      |
| `should_not_depend_on(target \| [target], directly=False)`   | Source must not import target(s); transitive by default                                                                  |
| `should_only_depend_on(allowed \| [allowed], directly=True)` | Every dependency must match the allow-list; direct by default. `"stdlib"` expands to any `sys.stdlib_module_names` entry |
| `ignoring(patterns)`                                         | fnmatch glob patterns skipped during chain traversal — alternate non-ignored paths still flag                            |
| `module(name, callback=None)`                                | Scope into a submodule (recursive, glob supported)                                                                       |
| `assert_arch.layers([...]).should_be_independent()`          | Strict layered architecture — each layer may only depend on layers preceding it in the list                              |
| `assert_arch.modules([...]).should_be_isolated()`            | Mutual isolation across an unordered set; combine with `ignoring(...)` to allow specific bridges                         |

## Layered architecture

```python
def test_layers_are_independent():
    assert_arch.layers([
        "myapp.domain",
        "myapp.application",
        "myapp.infrastructure",
    ]).should_be_independent()
```

Lower layers must not import higher ones. Skipping a layer downward (infra → domain directly) is allowed; only upward dependencies trigger a violation.

## Bounded-context isolation

```python
def test_bounded_contexts_are_isolated():
    assert_arch.modules([
        "proxysubscription", "accountsuspension", "referral",
    ]).should_be_isolated().ignoring(["*.events"])
```

No module in the set may depend on any other in either direction. `ignoring(["*.events"])` grandfathers cross-talk through published event modules — alternate paths through non-ignored modules still surface.

## Glob expansion

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

## Scoped callbacks

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

## Direct vs transitive

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

## Error messages

Failures surface the offending import chain so you know exactly where to fix:

```
AssertionError: shared should not depend on:
  - proxysubscription: shared → shared.auth.custom_basic_authentication → proxysubscription.models
```

Typo-style mistakes raise `ValueError` with a `Did you mean ...?` hint instead of a chain check.
