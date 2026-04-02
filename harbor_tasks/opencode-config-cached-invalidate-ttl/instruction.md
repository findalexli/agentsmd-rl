# Config cache invalidation uses mutable reassignment — non-idiomatic and silently swallows errors

## Problem

In `packages/opencode/src/config/config.ts`, the global config cache is implemented using a mutable `let` binding that gets reassigned every time `invalidate()` is called:

```ts
let cachedGlobal = yield* Effect.cached(loadGlobal().pipe(...))
// ...
// in invalidate():
cachedGlobal = yield* Effect.cached(loadGlobal().pipe(...))
```

This pattern has two issues:

1. **Non-idiomatic Effect usage**: The `let` + reassignment pattern bypasses Effect's built-in cache invalidation primitives. Effect provides proper APIs for cache invalidation that avoid mutable state entirely and are more correct under concurrent access.

2. **Silent error swallowing**: When `loadGlobal()` fails, the error is silently discarded via `Effect.orElseSucceed(() => ({}) as Info)` with no logging. This makes it very difficult to diagnose configuration loading failures in production — the system just silently falls back to empty defaults with no trace of what went wrong.

## Expected behavior

- The global config cache should use an idiomatic Effect cache invalidation primitive instead of mutable `let` reassignment
- Errors during global config loading should be logged before falling back to defaults
- The `invalidate` function should use the proper invalidation mechanism rather than recreating the cache from scratch

## Relevant files

- `packages/opencode/src/config/config.ts` — the `Config` namespace, specifically around line 1244 (cache creation) and line 1449 (invalidate function)
