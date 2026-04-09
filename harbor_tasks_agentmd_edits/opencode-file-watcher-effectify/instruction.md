# Effectify the FileWatcher service

## Problem

The file watcher in `packages/opencode/src/file/watcher.ts` is currently implemented as an imperative namespace (`FileWatcher`) using `Instance.state()` with raw async/await and `withTimeout`. This pattern doesn't compose well with the rest of the Effect-based codebase — it lacks structured concurrency, proper finalizers, and can't participate in the instance layer lifecycle.

Additionally, the `@parcel/watcher` and `node-pty` native addon callbacks fire outside the Node.js AsyncLocalStorage (ALS) context, which means `Instance.directory` and `Bus.publish` calls inside those callbacks silently read from the wrong (or no) instance context.

The two experimental flags `OPENCODE_EXPERIMENTAL_FILEWATCHER` and `OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER` in `packages/opencode/src/flag/flag.ts` are still plain `truthy()` booleans, but their consumer (the watcher) is moving to Effect and needs them as `Config<boolean>`.

## Expected Behavior

1. **Convert `FileWatcher` to an Effect service** (`FileWatcherService`) using the `ServiceMap.Service` pattern with a `static readonly layer`. The service should use `Effect.gen`, `Effect.addFinalizer` for cleanup, and `InstanceContext` instead of `Instance.*` globals. The existing `FileWatcher.Event` namespace must remain exported for backward compatibility.

2. **Add `Instance.bind(fn)`** on the `Instance` object in `packages/opencode/src/project/instance.ts` — a utility that captures the current ALS context and returns a wrapper restoring it when called. Use it to wrap native addon callbacks (the `@parcel/watcher` subscribe callback in the watcher and the `onData`/`onExit` callbacks in `packages/opencode/src/pty/index.ts`).

3. **Migrate the two watcher flags** from `truthy(...)` to `Config.boolean(...).pipe(Config.withDefault(false))` so they can be `yield*`-ed inside `Effect.gen`.

4. **Register `FileWatcherService`** in the instance layer system: add it to the `InstanceServices` union and `Layer.mergeAll(...)` in `packages/opencode/src/effect/instances.ts`, and update `packages/opencode/src/project/bootstrap.ts` to call the service via `runPromiseInstance`.

5. **Update `packages/opencode/AGENTS.md`** to document the new patterns introduced here: the `Effect.callback` API (renamed from `Effect.async`), the instance-scoped service registration pattern, `Instance.bind` for native callbacks, and the Flag → `Config.boolean` migration approach. These are important for future contributors working on Effect code in this package.

## Files to Look At

- `packages/opencode/src/file/watcher.ts` — the main file to refactor
- `packages/opencode/src/project/instance.ts` — add `Instance.bind`
- `packages/opencode/src/flag/flag.ts` — migrate two flags
- `packages/opencode/src/effect/instances.ts` — register the new service
- `packages/opencode/src/project/bootstrap.ts` — update init call
- `packages/opencode/src/pty/index.ts` — wrap native callbacks with `Instance.bind`
- `packages/opencode/AGENTS.md` — document the new patterns
