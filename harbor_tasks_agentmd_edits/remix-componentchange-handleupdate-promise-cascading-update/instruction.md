# Change handle.update() to return Promise<AbortSignal>

## Problem

The `handle.update()` API in the Remix component system currently accepts an optional task callback (`handle.update(task?)`). This leads to deeply nested callback soup when you need to perform sequential async work with intermediate UI updates:

```tsx
async function handler() {
  state = 'verifying'
  handle.update(signal => {
    let token = await fetchToken(signal)
    state = 'processing'
    handle.update(signal => {
      await process(token, signal)
      state = 'complete'
      handle.update()
    })
  })
}
```

Additionally, there is no protection against infinite cascading updates (e.g., calling `handle.update()` during a render), which can lock up the browser.

## Expected Behavior

1. `handle.update()` should return a `Promise<AbortSignal>` instead of accepting a task callback. The promise resolves when the update is complete (DOM is updated, tasks have run). The signal is aborted when the component updates again or is removed. This enables a flat async flow:

```tsx
async function handler() {
  state = 'verifying'
  let signal = await handle.update()
  let token = await fetchToken(signal)
  state = 'processing'
  signal = await handle.update()
  await process(token, signal)
  state = 'complete'
  handle.update()
}
```

2. The scheduler should detect infinite cascading updates (e.g., calling `handle.update()` inside a render function) and dispatch an error instead of looping forever.

3. After making the code changes, update the relevant documentation files (`AGENTS.md`, `README.md`, and docs) in `packages/component/` to reflect the new `handle.update()` API. The documentation should show the new `await` pattern and explain the `AbortSignal` return value. Remove or replace references to the old task callback pattern.

## Files to Look At

- `packages/component/src/lib/component.ts` — defines the `Handle` interface and `update()` implementation
- `packages/component/src/lib/scheduler.ts` — the flush/scheduling system that processes component updates
- `packages/component/AGENTS.md` — agent development guide with `handle.update()` documentation
- `packages/component/README.md` — package README with API reference for `handle.update()`
- `packages/component/docs/handle.md` — detailed handle API documentation
- `packages/component/src/test/` — existing test files that use `handle.update(task)` and need updating
