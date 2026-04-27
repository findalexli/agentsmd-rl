# Config cache invalidation uses mutable reassignment — non-idiomatic and silently swallows errors

## Problem

In `packages/opencode/src/config/config.ts`, the global config cache is implemented using a mutable `let` binding (`cachedGlobal`) that gets reassigned every time `invalidate()` is called. This pattern has two issues:

1. **Non-idiomatic Effect usage**: The `let` + reassignment pattern bypasses Effect's built-in cache invalidation primitives. Effect provides `cachedInvalidateWithTTL`, which returns both a cached value accessor and an invalidation handle — avoiding mutable state entirely and being more correct under concurrent access. The current code in `invalidate()` recreates the entire cached effect on every call via `Effect.cached(...)`, which is wasteful and error-prone.

2. **Silent error swallowing**: When `loadGlobal()` fails, the error is silently discarded via `orElseSucceed` with no logging whatsoever. This makes it very difficult to diagnose configuration loading failures in production — the system just silently falls back to empty defaults with no trace of what went wrong. Failures should be logged with the message "failed to load global config, using defaults" before the fallback takes effect.

## Expected behavior

- Replace the mutable `let cachedGlobal` + `Effect.cached(...)` pattern with `Effect.cachedInvalidateWithTTL`, which provides both a cached accessor and an invalidation handle
- The `invalidate()` function should use the returned invalidation handle instead of recreating the cache by reassignment
- Errors during config loading should be logged before the fallback to defaults, not silently swallowed

## Relevant files

- `packages/opencode/src/config/config.ts` — the `Config` namespace with `loadGlobal`, `getGlobal`, and `invalidate` functions

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
