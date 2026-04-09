# Fix useDeferredValue getting stuck

## Problem

`useDeferredValue` gets permanently stuck and never catches up to the current value. This happens when a suspended component's data resolves synchronously while React is already in the middle of a render cycle — for example, when a sibling component causes a suspended resource to resolve during its render.

The root cause is in `pingSuspendedRoot` in the reconciler work loop. When a ping arrives while a render is already in progress (`workInProgressRoot !== null`), the pinged lanes are not recorded. This means `markRootSuspended` later marks those lanes as suspended, and they are never retried. As a result, `useDeferredValue` never updates to the latest value.

## Expected Behavior

When a suspended resource resolves during an ongoing render, the reconciler should record the pinged lanes so they can be retried, allowing `useDeferredValue` to catch up to the latest value.

## Files to Look At

- `packages/react-reconciler/src/ReactFiberWorkLoop.js` — contains `pingSuspendedRoot` which handles notifying the scheduler when suspended data becomes available. Look at the branch where `workInProgressRoot !== null` (render is in progress).
