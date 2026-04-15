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

The global config cache should use `Effect.cachedInvalidateWithTTL` with the following specific implementation:

- Use `const [cachedGlobal, invalidateGlobal] = yield* Effect.cachedInvalidateWithTTL(...)` destructuring pattern (not `let cachedGlobal`)
- Import `Duration` from the 'effect' package and use `Duration.infinity` as the TTL argument
- Add `Effect.tapError` before `Effect.orElseSucceed` in the pipe chain to log errors before falling back to defaults
- The `invalidate` function should yield `invalidateGlobal` (the handle from destructuring) rather than reassigning `cachedGlobal`
- The `getGlobal` and `invalidate` functions should use `Effect.fn('Config.getGlobal')` and `Effect.fn('Config.invalidate')` named wrappers respectively

## Relevant files

- `packages/opencode/src/config/config.ts` — the `Config` namespace with `loadGlobal`, `getGlobal`, and `invalidate` functions
