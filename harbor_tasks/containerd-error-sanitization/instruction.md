# Task: Fix credential leak in error messages

## Problem

The containerd CRI (Container Runtime Interface) service is leaking sensitive credentials in error messages. When image pull operations fail, error messages returned via gRPC and logged may contain URL query parameters like `sig=SECRET_TOKEN` or `sv=2020-xxx` that expose authentication credentials.

## Your Task

1. Create a new utility function `SanitizeError` in `internal/cri/util/sanitize.go` that:
   - Accepts an error and returns an error
   - If the error contains a `*url.Error`, parses and sanitizes the URL
   - Redacts ALL query parameters from URLs (replace values with `[REDACTED]`)
   - Returns nil if input is nil
   - Returns the original error unchanged if it's not a URL error or has no query params
   - Returns a wrapped error that implements `Error()` and `Unwrap()` methods

2. Integrate this function into the CRI image service methods in `internal/cri/instrument/instrumented_service.go`:
   - `PullImage`
   - `ListImages`
   - `ImageStatus`
   - `RemoveImage`

   Call `SanitizeError` on any error before returning it.

## Example

An error like:
```
Get "https://storage.blob.core.windows.net/container/blob?sig=SECRET&sv=2020": connection timeout
```

Should be sanitized to:
```
Get "https://storage.blob.core.windows.net/container/blob?sig=[REDACTED]&sv=[REDACTED]": connection timeout
```

## Key Requirements

- The wrapped error must preserve error chain traversal (implement `Unwrap() error`)
- URL query parameters must be percent-encoded properly (e.g., `[REDACTED]` becomes `%5BREDACTED%5D`)
- The solution should handle nested/wrapped errors using `errors.As`
- Only URLs with query parameters should be modified; URLs without params pass through unchanged

## Files to Modify

- `internal/cri/util/sanitize.go` (create new)
- `internal/cri/instrument/instrumented_service.go` (modify)

## Hints

- Use `errors.As` to check if an error contains a `*url.Error`
- Use `url.Parse` and `url.Values` to properly handle URL query parameters
- Use `strings.ReplaceAll` in the `Error()` method to replace the original URL
- The `Unwrap()` method should return the original error for `errors.Unwrap()` to work
