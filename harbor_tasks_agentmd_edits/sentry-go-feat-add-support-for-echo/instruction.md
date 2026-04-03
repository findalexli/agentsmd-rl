# Upgrade Echo Integration from v4 to v5

## Problem

The `echo/` integration sub-module still depends on `github.com/labstack/echo/v4`. Echo v5 has been released with breaking API changes, and the Sentry echo middleware needs to be updated to support it.

Key v5 breaking changes that affect this integration:

1. **Pointer-based Context**: `echo.Context` is now a concrete `*echo.Context` pointer instead of an interface. All handler signatures and public API functions that accept `echo.Context` must be updated.
2. **Response access**: `ctx.Response()` now returns `http.ResponseWriter`, not `*echo.Response`. To get the underlying `*echo.Response` (e.g. for status code), you need `echo.UnwrapResponse()`.
3. **Error type handling**: The unexported `*httpError` type (used by `ErrNotFound`, `ErrMethodNotAllowed`, etc.) doesn't match `*echo.HTTPError`. Use the `echo.HTTPStatusCoder` interface instead.
4. **Nil handler panic**: Echo v5's router panics when registering a nil handler function.

## Expected Behavior

- `echo/go.mod` requires `github.com/labstack/echo/v5` with Go 1.25+
- `sentryecho.go` compiles against Echo v5 — all handler and public API signatures use `*echo.Context`
- Response status extraction uses `echo.UnwrapResponse()` and gracefully handles cases where unwrapping fails (status should be 0, not a default 200)
- Error status extraction uses the `echo.HTTPStatusCoder` interface
- All existing tests pass with the updated API, including proper handling of nil handlers in test setup
- The `echo/README.md` documentation and `example_test.go` examples are updated to reflect the new v5 API (import paths, handler signatures)

## Files to Look At

- `echo/sentryecho.go` — the Sentry Echo middleware implementation
- `echo/go.mod` — module dependencies
- `echo/sentryecho_test.go` — integration tests
- `echo/example_test.go` — example functions used in godoc
- `echo/README.md` — usage documentation with code examples
