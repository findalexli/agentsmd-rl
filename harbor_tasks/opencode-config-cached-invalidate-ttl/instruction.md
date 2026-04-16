# Config cache invalidation uses mutable reassignment — non-idiomatic and silently swallows errors

## Problem

In `packages/opencode/src/config/config.ts`, the global config cache is implemented using a mutable `let` binding that gets reassigned every time `invalidate()` is called. This pattern has two issues:

1. **Non-idiomatic Effect usage**: The `let` + reassignment pattern bypasses Effect's built-in cache invalidation primitives. Effect provides proper APIs for cache invalidation that avoid mutable state entirely and are more correct under concurrent access.

2. **Silent error swallowing**: When `loadGlobal()` fails, the error is silently discarded with no logging. This makes it very difficult to diagnose configuration loading failures in production — the system just silently falls back to empty defaults with no trace of what went wrong.

## Expected behavior

The global config cache must use `Effect.cachedInvalidateWithTTL` with the following specific implementation requirements:

- Import `Duration` from the 'effect' package
- The cache initialization must use `Effect.cachedInvalidateWithTTL` with two return values captured via destructuring — one for accessing the cached value and one for invalidating it
- Use `Duration.infinity` as the TTL argument to `cachedInvalidateWithTTL`
- Errors during config loading must be logged via `Effect.tapError` before falling back to defaults. Specifically, `tapError` must come before `orElseSucceed` in the pipe chain, and the error handler should log: `"failed to load global config, using defaults"` along with the stringified error
- The `invalidate` function must yield the invalidation handle (the second value from destructuring) rather than recreating the cache
- The `getGlobal` function must be wrapped with `Effect.fn('Config.getGlobal')`
- The `invalidate` function must be wrapped with `Effect.fn('Config.invalidate')`

## Relevant files

- `packages/opencode/src/config/config.ts` — the `Config` namespace with `loadGlobal`, `getGlobal`, and `invalidate` functions
