# Task: Fix Content Storage Pollution in Docker Resolver

## Problem

The containerd Docker resolver has a bug that can permanently corrupt local image storage. When resolving an image reference by digest, the resolver queries the `/manifests/` endpoint. If this endpoint returns a **transient error** (like HTTP 500, 502, or 503), the resolver incorrectly falls back to the `/blobs/` endpoint.

The `/blobs/` endpoint always returns `application/octet-stream` as the content type, regardless of what the actual content is. When this wrong media type gets cached in containerd's metadata store, the image becomes permanently "poisoned" - subsequent operations on that image reference will fail because the descriptor has the wrong media type.

## Expected Behavior

- **404 Not Found** from `/manifests/` -> should fall back to `/blobs/` (backward compatibility with legacy registries)
- **5xx Server Errors** from `/manifests/` -> should return the error immediately, **do NOT fall back to `/blobs/`**

When 5xx errors occur, the resolver should return errors of type `ErrUnexpectedStatus` with the appropriate HTTP status code (500, 502, 503) from the package `github.com/containerd/containerd/v2/core/remotes/errors`.

## Where to Fix

The bug is in `core/remotes/docker/resolver.go`. Look at the path resolution loop where the resolver tries multiple paths when resolving a reference. The `/manifests/` path is tried first, then the resolver falls back to `/blobs/`. The problem is that this fallback currently happens for ALL errors, including transient server errors (5xx), when it should only happen for "not found" type errors (4xx).

The code tracks error severity using a priority system. Errors with higher priority (transient server errors like 5xx) should prevent fallback to `/blobs/`, while lower priority errors (like 404) should allow fallback for backward compatibility.

## Symptoms

- Images intermittently fail to pull with "unsupported media type" errors
- Content store contains descriptors with `application/octet-stream` instead of proper manifest media types
- Issues correlate with transient registry errors (5xx responses)
- The error manifests as `ErrUnexpectedStatus` from the `github.com/containerd/containerd/v2/core/remotes/errors` package

## Testing Your Fix

You can verify your fix by:

1. Running the existing Go tests: `go test ./core/remotes/docker/...`
2. Checking that code compiles: `go build ./core/remotes/docker/...`
3. Creating a test that simulates a 500 error from `/manifests/` and verifies `/blobs/` is NOT called
4. Verifying that 404 errors still correctly trigger fallback to `/blobs/`

## References

- Issue #13007 describes the content store pollution symptom
- The resolver handles both `/manifests/` and `/blobs/` endpoints

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `gofmt (Go formatter)`
