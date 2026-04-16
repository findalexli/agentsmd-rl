# Fix Arrow Binding Behavior When Dragging Endpoints

## Problem

When an arrow has one endpoint with a "fixed" binding (inside an element, created with Alt/Option key), dragging the OTHER endpoint incorrectly converts the fixed binding to an "orbit" binding. The fixed binding should be preserved.

## Symptoms

1. Create an arrow with one end bound "inside" an element (using Alt key during creation)
2. Drag the OTHER endpoint of the arrow
3. The inside binding incorrectly becomes an orbit binding

## Files to Investigate

- `packages/element/src/binding.ts` - Contains the binding strategy logic
  - Look at `getBindingStrategyForDraggingBindingElementEndpoints_simple` function
  - The issue is in how the "other" binding strategy is determined

- `packages/excalidraw/components/App.tsx` - Handles arrow creation
  - Look at how arrow binding state is tracked during creation
  - The `initialState` of `LinearElementEditor` may need additional tracking

## Context

The binding system has two main modes:
- `"inside"` (fixed): Arrow endpoint is fixed inside an element (created with Alt key)
- `"orbit"`: Arrow endpoint orbits around the element boundary

When dragging one endpoint, the code currently doesn't check if the OTHER endpoint has an "inside" binding before potentially converting it to "orbit".

## Requirements

1. When one endpoint has an "inside" binding and you drag the other endpoint, the inside binding should remain unchanged
2. The binding logic must detect when the OTHER endpoint already has a `"inside"` mode binding (via `otherBinding?.mode === "inside"`) and preserve it
3. The fix requires:
   - A flag tracking whether the arrow start has an inside binding (stored in `initialState` with key `arrowStartIsInside`)
   - A variable (named `otherNeverOverride`) that determines when to skip overriding the other endpoint's binding
   - When `otherNeverOverride` is true, the other endpoint's binding mode should remain `{ mode: undefined }`
   - The logic `const other: BindingStrategy = !otherNeverOverride ? ... : { mode: undefined }` gates whether the orbit conversion is applied
4. TypeScript compilation and tests should still pass