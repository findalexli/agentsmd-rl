# Fix Bound Arrow Element Updates

## Problem

There are two scenarios where bound arrow elements fail to update correctly:

### 1. Distribute Action
When using the "distribute elements" feature on elements that have arrows bound to them, the arrows don't render in the correct position until the elements are manually moved.

The `distributeElements` function in `packages/element/src/distribute.ts` currently uses `newElementWith()` to update element positions, but this doesn't trigger updates to the bound arrows. Looking at the `alignElements` function (fixed in PR #8998), you can see the correct pattern: use `scene.mutateElement()` followed by `updateBoundElements()`.

### 2. Text Overflow in WYSIWYG Editor
When text bound to a container extends beyond the container's height (causing the container to auto-expand), the associated arrow elements don't update their positions.

In `packages/excalidraw/wysiwyg/textWysiwyg.tsx`, when the container height is updated via `app.scene.mutateElement(container, { height: targetContainerHeight })`, the bound arrows aren't notified of the change.

## Expected Fix

1. **For distributeElements**: Refactor to use `scene.mutateElement()` and call `updateBoundElements()` after each mutation. The function needs to accept a `scene: Scene` parameter (similar to how `alignElements` works).

2. **For textWysiwyg**: Add `updateBoundElements(container, app.scene)` calls after each `mutateElement` call that updates container height.

## Files to Modify

- `packages/element/src/distribute.ts` - Core distribution logic
- `packages/excalidraw/actions/actionDistribute.tsx` - Pass scene parameter
- `packages/excalidraw/wysiwyg/textWysiwyg.tsx` - Update bound arrows on height change

## Key API References

- `updateBoundElements(element, scene, options?)` from `@excalidraw/element` - updates arrows bound to an element
- `scene.mutateElement(element, updates)` - mutates an element and notifies the scene

## Testing

Run `yarn test:typecheck` to ensure TypeScript compiles correctly after your changes.

## Additional Context

The fix for the align action in PR #8998 demonstrates the correct pattern to follow. The distribute action was missed during that refactor and still uses the old `newElementWith` approach.
