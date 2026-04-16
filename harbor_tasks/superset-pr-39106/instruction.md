# MCP Auth Layer: Unsafe g.user Fallback on JWT Resolution Failure

## Problem

The MCP (Model Context Protocol) authentication layer in `superset/mcp_service/auth.py` has a security vulnerability in the `_setup_user_context()` function.

When `get_user_from_request()` raises a `ValueError` (e.g., when a SAML subject is not found in the database), the exception handler does **not** deny the request. Instead, it falls back to `g.user` from Flask middleware. Specifically, the buggy ValueError handler:

- Checks for `g.user` and assigns `user = g.user` as a fallback identity
- Uses a `break` statement to exit the retry loop and continue processing
- Logs a warning containing the string `"falling back to middleware-provided"`

This allows a request with an unresolvable JWT to proceed authenticated as whichever user the middleware set in `g.user`.

## Security Impact

In multi-tenant deployments, if JWT resolution fails for "user A", the request silently proceeds as whoever `g.user` was set to by middleware. This could allow a request to be authenticated as the wrong user.

## Required Behavior

The ValueError handler must be fail-closed. The correct handler:

1. **Must re-raise the ValueError** — no fallback, no `break` statement, and no `user = g.user` assignment.
2. **Must clear the middleware-provided identity** — call `g.pop("user", None)` so error/audit logging does not attribute the denied request to the middleware user.
3. **Must log at error level** — the log message must contain the string `"MCP user resolution failed"`. The string `"falling back to middleware-provided"` must not appear anywhere in the file.
4. **Must clean up on DB connection retry failure** — in the OperationalError handler, when retries are exhausted (the code logs `"DB connection failed on retry during user setup"`), the function `_cleanup_session_on_error()` must be called before re-raising.

## Constraints

- The modified file must have valid Python syntax.
- The file must pass the project's `ruff check` and `ruff format --check` linter rules.
