# Task: Add Security Validation for Reconnect URLs

## Problem

The LangGraph SDK's HTTP client follows `Location` headers when reconnecting to streaming endpoints. Currently, the SDK does NOT validate these redirect URLs, which could lead to credential leakage if a malicious server responds with a cross-origin `Location` header pointing to an attacker-controlled server.

When the SDK receives a reconnect response with a `Location` header, it follows the redirect without verifying that the target URL shares the same origin (scheme, host, and port) as the original API request. This could allow credentials to be sent to external servers.

## Goal

Add validation to ensure that `Location` headers in reconnect responses match the origin of the base API URL. Cross-origin redirects should be rejected with a clear error message.

## Requirements

1. **Validation Logic** — Before following any `Location` header during reconnection, the SDK must validate that the URL is same-origin as the base API URL:
   - Relative URLs (paths without scheme/host) should be allowed
   - Same-origin URLs (matching scheme, host, and port) should be allowed
   - Default ports must be normalized so implicit and explicit defaults are treated as equivalent (e.g., `https://api.example.com` and `https://api.example.com:443` are the same origin; `http://api.example.com` and `http://api.example.com:80` are the same origin)
   - Cross-origin URLs (different scheme, host, or port) must raise a `ValueError` with a message containing the word "cross-origin" or "refusing"

2. **Port Handling** — The validation must correctly handle default ports:
   - HTTPS default port: 443
   - HTTP default port: 80

3. **Integration Points** — The validation must be applied:
   - In the async HTTP client's reconnect handling
   - In the sync HTTP client's reconnect handling
   - Wherever `Location` headers from reconnect responses are processed

4. **Version Update** — Set `__version__` in `langgraph_sdk/__init__.py` to `"0.3.13"`.

## Code Style Requirements

- In docstrings and comments across all modified files, do not use four consecutive backticks on each side of a word (pattern: ````word````). Use single backticks only.
- Before submitting, run `make format` (code formatters) and `make lint` (linter) in `libs/sdk-py/`.

## Testing

Before submitting, run the following command in `libs/sdk-py/`:
- `make test` — execute the test suite

## Notes

- The `httpx.URL` class provides `.scheme`, `.host`, and `.port` attributes
- Python's `urllib.parse.urlparse` can parse Location header strings
- The `Location` header is retrieved via `response.headers.get("location")`
- Reconnection logic is found in the HTTP client implementations for both async and sync variants
