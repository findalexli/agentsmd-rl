# Fix: Prevent Credential Leak in CRI Image Operation Errors

## Problem

When CRI (Container Runtime Interface) image operations fail, the error messages returned via gRPC may contain sensitive information such as Azure Blob Storage SAS tokens or other credentials embedded in URLs. This is a security vulnerability as these credentials could be exposed in pod events, logs, or error responses.

For example, if an image pull from a registry URL like `https://storage.blob.core.windows.net/container/blob?sig=SECRET_TOKEN&sv=2020` fails due to a network error, the error message containing the full URL with the secret signature parameter may be returned to the client and logged.

## Goal

Implement a solution that sanitizes errors before they are returned via gRPC in the CRI image operations. The solution should:

1. Detect when an error contains URL information (specifically `*url.Error`)
2. Parse and sanitize the URL by redacting all query parameter values with the literal string `[REDACTED]`
3. Preserve the original error structure so it can still be unwrapped
4. Handle edge cases like nil errors, non-URL errors, and URLs without query parameters

## Required Test Names

The implementation must include comprehensive tests with these exact function names:

- `TestSanitizeError_SimpleURLError` - Tests that URL errors with sensitive query params are sanitized
- `TestSanitizeError_WrappedError` - Tests that wrapped errors (e.g., `fmt.Errorf("pull failed: %w", urlErr)`) are properly handled
- `TestSanitizeError_NilError` - Tests that nil errors pass through unchanged
- `TestSanitizeError_NonURLError` - Tests that non-URL errors pass through unchanged
- `TestSanitizeError_NoQueryParams` - Tests that URL errors without query params pass through unchanged
- `TestSanitizedError_Unwrap` - Tests that the sanitized error correctly unwraps to the original error

## Integration Requirement

The CRI image operations are instrumented and errors from these operations must be sanitized before they are converted to gRPC format. The image operations include: PullImage, ListImages, ImageStatus, and RemoveImage.

After implementing the fix, errors from image operations should be processed by a sanitization function before being passed to the gRPC error conversion. The string `ctrdutil.SanitizeError(err)` must appear in the codebase as evidence of this integration.

## Testing

The tests should verify that:
- Sensitive tokens like `sig=SECRET` are replaced with `sig=[REDACTED]`
- The error message structure is preserved (wrapper messages are kept)
- The error can still be unwrapped to access the original `*url.Error`
- Nil and non-URL errors pass through unchanged
- The code compiles and passes `go vet` and `go fmt` checks
