# Fix: Angle locking ignored during linear element endpoint binding

## Problem

In the Excalidraw codebase at `/workspace/excalidraw`, when creating or editing
a linear element (arrow/line) and holding Shift to constrain the angle to
discrete values (15-degree increments), the angle constraint is lost when the
endpoint is near a bindable element. The expected behavior is that Shift should
constrain angles even when the endpoint snaps to a binding target.

## Context

The issue involves the interaction between angle locking (Shift key behavior)
and element binding in the linear element editor. The relevant code spans these
files:

- `packages/element/src/binding.ts` — binding strategy functions:
  `bindOrUnbindBindingElement` and
  `getBindingStrategyForDraggingBindingElementEndpoints`
- `packages/element/src/linearElementEditor.ts` — endpoint drag handling
  in the `LinearElementEditor` class, particularly the `pointDraggingUpdates`
  helper function
- `packages/excalidraw/actions/actionFinalize.tsx` — element finalization
  action
- `packages/excalidraw/components/App.tsx` — new arrow creation flow

## Symptoms

1. In `linearElementEditor.ts`, the angle-lock condition calls
   `shouldRotateWithDiscreteAngle(event)` but also requires that there be no
   hovered binding target and no existing start/end bindings on the element.
   These extra conditions disable angle locking whenever any binding context is
   present — the angle constraint should apply regardless of binding state.

2. The `pointDraggingUpdates` function passes raw `event.shiftKey` to the
   binding strategy, but the binding logic needs the computed angle-lock state
   (the result of `shouldRotateWithDiscreteAngle`) rather than the raw key
   state, so it can make proper binding decisions.

3. The `getBindingStrategyForDraggingBindingElementEndpoints` function
   receives a `shiftKey` option but has no way to handle the angle-locked case
   for the non-dragged endpoint's binding — it needs an `angleLocked` option
   that triggers orbit mode binding with a focus point computed via
   `projectFixedPointOntoDiagonal`.

4. The callers of `bindOrUnbindBindingElement` in `actionFinalize.tsx` and
   `App.tsx` also need to pass the computed angle-lock state (using
   `shouldRotateWithDiscreteAngle`) rather than raw key state.

## Expected Fix

1. Simplify the angle-lock conditions in `linearElementEditor.ts` so the
   discrete-angle rotation applies based only on
   `shouldRotateWithDiscreteAngle(event)`, without gating on hovered elements
   or existing bindings.

2. Refactor the parameter passing through the binding call chain: replace the
   raw `shiftKey` parameter with an `angleLocked` boolean that carries the
   result of `shouldRotateWithDiscreteAngle`. The parameter name should be
   `angleLocked` in the `pointDraggingUpdates` function signature, the opts
   types in `bindOrUnbindBindingElement` and
   `getBindingStrategyForDraggingBindingElementEndpoints`, and all call sites.

3. In the binding strategy, when `angleLocked` is true and there is a bindable
   element for the other (non-dragged) endpoint, compute the other endpoint
   position using `LinearElementEditor.getPointAtIndexGlobalCoordinates` and
   use orbit mode with a focus point from `projectFixedPointOntoDiagonal`.

## Validation

After the fix, all of the following should pass:

- TypeScript type checking: `yarn test:typecheck`
- ESLint: `yarn test:code`
- Prettier: `yarn test:other`
- Binding tests: `yarn test:app packages/element/tests/binding.test.tsx --watch=false`
- Linear element editor tests: `yarn test:app packages/element/tests/linearElementEditor.test.tsx --watch=false`
- Elbow arrow tests: `yarn test:app packages/element/tests/elbowArrow.test.tsx --watch=false`
