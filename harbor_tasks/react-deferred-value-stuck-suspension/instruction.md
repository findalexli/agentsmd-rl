# useDeferredValue gets stuck after state update with Suspense

## Problem

When a component uses `useDeferredValue` together with a `<Suspense>` boundary, the deferred value can get permanently stuck at the old value after a state update. The UI never catches up to show the new value, even after the suspended resource resolves.

Specifically, when a suspension is resolved synchronously during the same render pass (e.g., a sibling component resolves the data while rendering), React fails to retry the suspended render. The pinged lanes are not recorded, so `markRootSuspended` marks them as suspended and they are never retried.

## Expected Behavior

After a state update triggers a new render with `useDeferredValue`, the deferred value should eventually catch up and reflect the latest value. Synchronous pings that arrive during an ongoing render should be recorded so the corresponding lanes can be retried.

## Files to Look At

- `packages/react-reconciler/src/ReactFiberWorkLoop.js` — the `pingSuspendedRoot` function handles what happens when a suspended root receives a ping (resource resolved). When the root is currently rendering, the pinged lanes need to be recorded so they are not incorrectly marked as suspended.
