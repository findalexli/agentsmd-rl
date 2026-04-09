# Task: Fix gRPC Authorization Bypass Vulnerability

## Problem

The containerd project uses gRPC for its API. There's a security vulnerability in the vendored gRPC library (version 1.79.2) where malformed `:path` headers missing the leading slash (`/`) could bypass path-based restricted "deny" rules in interceptors like `grpc/authz`.

For example, a request to `service/method` (without leading slash) could bypass security policies that expect `/service/method` format.

## Your Task

Apply the security fix to prevent this authorization bypass. The fix has been released in gRPC 1.79.3 and involves:

1. **Add strict path checking to the gRPC server** - Reject requests with malformed method names
2. **Add an envconfig option** - Allow temporary opt-out via environment variable for migration
3. **Update version strings** - Reflect the new gRPC version

## Files to Modify

The fix should be applied to the vendored gRPC code:

- `vendor/google.golang.org/grpc/internal/envconfig/envconfig.go` - Add `DisableStrictPathChecking` option
- `vendor/google.golang.org/grpc/server.go` - Add strict path validation in `handleStream` method
- `vendor/google.golang.org/grpc/version.go` - Update version constant
- `go.mod` and `go.sum` - Update gRPC dependency version
- `vendor/modules.txt` - Update version comment

## Requirements

1. **Strict path checking must be enabled by default** - Requests with paths not starting with `/` should be rejected with an `Unimplemented` error
2. **Empty method names must be rejected** - Handle this as a malformed request
3. **Add helper function** - Create `handleMalformedMethodName` to handle error responses consistently
4. **Add environment variable opt-out** - Support `GRPC_GO_EXPERIMENTAL_DISABLE_STRICT_PATH_CHECKING` to temporarily allow non-compliant requests (for migration only)
5. **Add proper logging** - Log warnings when rejecting or allowing malformed paths
6. **Update version** - Change version from `1.79.2` to `1.79.3`

## Hints

- Look at the `handleStream` function in `server.go` to understand how method names are currently processed
- The method name processing currently strips the leading `/` if present - this needs to change to reject requests without it
- Consider adding a new field to the `Server` struct to track whether the warning log has been emitted (to avoid spam)
- The fix should use the existing `codes.Unimplemented` status code for rejected requests

## Expected Behavior

After the fix:
- Requests to `/service/method` work normally
- Requests to `service/method` (no leading slash) are rejected with `Unimplemented` error
- Empty method names are rejected with `Unimplemented` error
- The code compiles successfully
