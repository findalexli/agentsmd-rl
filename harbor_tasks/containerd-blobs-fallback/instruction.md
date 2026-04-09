# Task: Fix containerd resolver fallback behavior

## Problem

The containerd Docker registry resolver has a bug where transient server errors (5xx) from the `/manifests/` endpoint cause it to fall back to the `/blobs/` endpoint. This fallback can permanently corrupt images in the local content store because:

1. The `/blobs/` endpoint always returns `Content-Type: application/octet-stream`
2. This overwrites the proper manifest media type in the descriptor
3. The corrupted descriptor then poisons the content store

## Example scenario

1. Registry returns 500 Internal Server Error for `/manifests/<digest>`
2. Resolver falls back to `/blobs/<digest>`
3. `/blobs/` returns the manifest content but with `application/octet-stream`
4. Descriptor is stored with wrong media type
5. Content store now has incorrectly typed content

## Expected behavior

- **404 from `/manifests/`**: Should fall back to `/blobs/` (backward compatibility for legacy registries)
- **5xx or other transient errors**: Should NOT fall back to `/blobs/` - return the error instead

## Where to look

The relevant code is in `core/remotes/docker/resolver.go` in the `Resolve()` function. Look for the loop that iterates over `paths` and the fallback logic between endpoints.

The key insight is that errors have different priorities:
- "Not found" errors (priority <= 2) can trigger fallback
- Server/transient errors (priority > 2) should not trigger fallback

## What you need to do

1. Understand the current fallback logic in `resolver.go`
2. Add a check to prevent fallback to `/blobs/` when the error is a transient/server error
3. Ensure the fix still allows fallback for 404/not-found errors
4. Run the tests to verify your fix works

## Testing

The repository has existing tests in `core/remotes/docker/resolver_test.go`. You can run them with:

```bash
cd /workspace/containerd
go test -v -run "TestResolve" ./core/remotes/docker/
```

There are two key test cases to verify:
- `TestResolveTransientManifestError`: Verifies 5xx doesn't trigger fallback (fail-to-pass)
- `TestResolve404ManifestFallback`: Verifies 404 still allows fallback (pass-to-pass)
