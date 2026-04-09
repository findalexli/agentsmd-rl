# Fix Angle Locking for Linear Element Binding

## Problem

When dragging a linear element (arrow or line) endpoint with the **Shift key held** to constrain the angle to discrete values (45° increments), the angle lock **stops working** when the endpoint is being bound to another element.

The angle should remain constrained to discrete angles (0°, 45°, 90°, etc.) even when the endpoint is being attached to a bindable element (like a rectangle). Currently, the binding logic overrides the angle constraint.

## Affected Files

The bug is in the binding logic for linear elements. The key files involved are:

1. **`packages/element/src/binding.ts`** - Contains the core binding strategy logic
   - `bindOrUnbindBindingElement()` - Main entry point for binding operations
   - `getBindingStrategyForDraggingBindingElementEndpoints()` - Determines how to handle binding during drag operations

2. **`packages/element/src/linearElementEditor.ts`** - Handles linear element editing
   - `LinearElementEditor` class - Manages arrow/line editing interactions
   - Look for shift key handling around point dragging logic

3. **`packages/excalidraw/actions/actionFinalize.tsx`** - Finalizes arrow creation/editing
   - Calls binding functions when finishing arrow drawing

4. **`packages/excalidraw/components/App.tsx`** - Main app component
   - Handles initial arrow binding during creation

## Expected Behavior

When a user:
1. Creates or edits an arrow
2. Holds Shift to lock the angle
3. Drags an endpoint near a bindable element

The arrow should:
- Remain at a discrete angle (0°, 45°, 90°, 135°, etc.)
- Still bind to the target element correctly

Currently, the angle lock is lost when binding activates.

## Technical Context

- The function `shouldRotateWithDiscreteAngle(event)` checks if angle locking should be active
- The binding system uses `getBindingStrategyForDraggingBindingElementEndpoints()` to decide how to bind endpoints
- When angle lock is active, the "other" endpoint (the one not being dragged) should use "orbit" binding mode while maintaining the angle constraint
- The function `projectFixedPointOntoDiagonal()` can project a point onto a diagonal line at a discrete angle

## Hints

1. The binding functions accept an `opts` parameter that can be extended to pass additional state
2. Look for where `shiftKey` is currently passed to binding functions - this should be replaced with a more explicit `angleLocked` flag
3. The binding strategy needs to know about angle locking to properly handle the "other" endpoint's binding mode
4. There may be over-restrictive checks in the linear element editor that prevent angle locking when bindings exist

## Testing

After your changes:
1. Run `yarn test:typecheck` to verify TypeScript compiles
2. The code should allow angle-locked binding behavior

## Project Info

- This is a TypeScript monorepo using Yarn workspaces
- Key packages: `@excalidraw/common`, `@excalidraw/element`, `@excalidraw/excalidraw`
- Run `yarn install` to install dependencies
- Run `yarn test:typecheck` to check TypeScript
