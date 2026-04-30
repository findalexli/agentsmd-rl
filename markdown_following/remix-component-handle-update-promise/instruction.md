# handle.update() Promise API + Cascading Update Guard

## Problem

The `handle.update(task?)` API in the Remix component framework accepts an optional task callback that runs after the update completes. This leads to deeply nested callback soup when multiple sequential updates are needed (each requiring a task for the next step).

Additionally, calling `handle.update()` during a render function creates an infinite loop that is never caught, potentially freezing the browser.

## Expected Behavior

1. **API change**: `handle.update()` should no longer accept a task callback. Instead, it should return a `Promise<AbortSignal>` that resolves after the update completes. The returned signal is aborted when the component updates again or is removed. This allows callers to `await handle.update()` and use the signal for further async work.

2. **Cascading update guard**: The scheduler must detect and stop infinite cascading update loops (e.g., when `handle.update()` is called during a render function). When cascading updates exceed a threshold during a single flush, the scheduler must report an error with the message `"infinite loop detected"`.

3. **Cleanup**: When a component is removed, cleanup must also be performed for any render-level controller. The `remove()` function must abort this controller.

## Files to Look At

- `packages/component/src/lib/component.ts` — The `Handle` interface and `createComponent` function. The `update` method signature and implementation need to change. The `remove()` function needs to perform additional cleanup.
- `packages/component/src/lib/scheduler.ts` — The `flush()` function needs cascading update protection.
- `packages/component/AGENTS.md` — Agent guide that documents the Handle API. Must be updated to reflect the new Promise-based `handle.update()` signature and usage patterns.
- `packages/component/README.md` — Package README with API reference. Must be updated for the new `handle.update()` signature.
- `packages/component/docs/handle.md` — Dedicated handle documentation. Must be updated for the new API.

## Important Notes

- This is a breaking API change. The old `handle.update(task)` callback pattern is replaced with `await handle.update()` returning a signal.
- The `handle.queueTask()` method still works as before for synchronous DOM operations that must happen during the flush.
- After implementing the code changes, update the relevant documentation files (AGENTS.md, README.md, docs/handle.md) to reflect the new API. Remove references to the old task callback pattern and document the Promise-based approach instead.
- Existing test files in `src/test/` that call `handle.update(task)` will also need updating to use the new API.