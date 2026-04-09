# Fix useDeferredValue getting stuck

## Problem

When using `useDeferredValue` with `Suspense`, the deferred value can get permanently stuck on a stale value. This happens specifically when a suspended resource is resolved **during the same render** — for example, a sibling component resolves a cache entry while React is still rendering the current tree.

After a state update, the deferred value never catches up to the current value. The UI remains frozen showing the old deferred content instead of updating to reflect the new state.

## Expected Behavior

When a suspension is resolved mid-render (via a synchronous ping), React should record that information and retry the render so the deferred value can catch up to the current value.

## Files to Look At

- `packages/react-reconciler/src/ReactFiberWorkLoop.js` — Contains `pingSuspendedRoot`, the function that handles suspension resolution notifications. Look at how it behaves when a ping arrives during an active render phase versus outside of it.
