# Fix crash when rendering a new class component while simulating errored state in DevTools

## Problem

React DevTools allows developers to force error boundaries into their error state by using "Force Error" in the component inspector. However, there is a crash when:

1. A class component that is **not** an error boundary is placed inside an error boundary
2. DevTools forces an error on that inner class component
3. The error is then toggled **off**

When DevTools toggles off the simulated error, the reconciler's `updateClassComponent` function assumes the component's `stateNode` (instance) has already been constructed. But if the component was first rendered as a result of simulating the errored state, the instance may not exist yet, causing a crash when the reconciler tries to access it.

The root cause is in the DevTools backend: the `shouldErrorFiberAccordingToMap` function in `renderer.js` returns the wrong value for fibers that were never in the force-error map, causing the reconciler to incorrectly treat them as previously-errored boundaries that need resetting.

## Expected Behavior

Toggling "Force Error" off on any class component (even one that isn't an error boundary) should not crash. The reconciler should only attempt to reset error state on fibers that were genuinely previously in the force-error map — not on every class component.

## Files to Look At

- `packages/react-devtools-shared/src/backend/fiber/renderer.js` — contains `shouldErrorFiberAccordingToMap`, which determines whether a fiber should be forced into an error state. Look at what it returns for fibers that have no entry in the map.
- `packages/react-reconciler/src/ReactFiberBeginWork.js` — contains `updateClassComponent`, which uses a `switch` on `shouldError(workInProgress)` to decide whether to force or reset an error. The `case false:` branch assumes the instance exists.
