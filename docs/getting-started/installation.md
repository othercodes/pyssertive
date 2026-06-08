# Installation

## Requirements

- Python 3.10+
- Django 4.2, 5.2, or 6.0 (optional, only if using the Django adapter)
- httpx 0.27+ (optional, only if using the httpx adapter for FastAPI/Starlette/FastMCP)

## Install

```bash
pip install pyssertive            # core
pip install pyssertive[django]    # with Django adapter
pip install pyssertive[httpx]     # with httpx adapter (FastAPI, Starlette, FastMCP)
```

The core package brings the generic [`expect`](../guides/expectations.md) vocabulary
plus the JSON, HTML, MCP, and architecture assertables. The `[django]` and `[httpx]`
extras add the HTTP test clients and request builders for each framework.
