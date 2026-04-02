# Plugin service bypasses Effect's structured error handling

## Context

The Plugin service in `packages/opencode/src/plugin/index.ts` manages loading internal and external plugins, calling their hooks, and composing them into the Effect layer graph.

## Problem

The Plugin service's `InstanceState.make` closure wraps nearly all its logic inside a single `Effect.promise(async () => { ... })`. This has several consequences:

1. **Lost structured errors**: Plugin loading failures are caught with bare `try/catch` or `.catch()` instead of using Effect's `tryPromise` + typed error channels. This means plugin errors don't flow through Effect's error system.

2. **Async facade leakage**: Inside the `Effect.promise` block, the code calls `Config.get()` and `Config.waitForDependencies()` — these are async convenience facades. Since the code is already in an Effect generator, it should yield the `Config.Service` directly and call methods on the yielded instance. Similarly, `Bus.publish()` (the async facade) is used for error reporting instead of the yielded `bus` service.

3. **Batched hook triggering**: The `trigger` helper wraps all hook calls in one `Effect.promise(async () => { for ... await fn() })`. If a hook errors, it breaks the loop. Each hook invocation should be its own `yield* Effect.promise(...)` call.

4. **Missing layer dependency**: Because `Config.Service` should be yielded directly in the generator (rather than accessed via the async facade), the `Config.defaultLayer` needs to be provided to the Plugin's `defaultLayer` composition. Currently it only provides `Bus.layer`.

5. **Error isolation for config hooks**: The loop notifying plugins of the current config uses `try/catch`. This should use `Effect.tryPromise` piped through `Effect.ignore` for proper Effect-native error isolation.

## Files to modify

- `packages/opencode/src/plugin/index.ts` — the main Plugin service implementation
- `packages/opencode/test/plugin/auth-override.test.ts` — update the error isolation test to match the new Effect patterns

## Guidance

- Refer to `packages/opencode/AGENTS.md` for the project's Effect conventions (Effect.fn, Effect.tryPromise, InstanceState patterns).
- The `trigger` function should yield each hook individually rather than batching them in a single promise.
- The test in `auth-override.test.ts` has a regex that validates the error isolation pattern — it will need updating to match Effect.tryPromise + Effect.ignore instead of try/catch.
