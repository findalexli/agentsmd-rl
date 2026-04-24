# Bound Arrow Elements Not Updated After Element Mutations

In Excalidraw, shape elements can have bound arrows attached to them. When a shape is moved or resized, its bound arrows must be repositioned to stay attached. The `updateBoundElements` function handles this.

## Bug

Two code paths mutate elements but do not update bound arrows afterward, causing arrows to become detached from their target shapes:

1. **Element distribution** - When selected elements are evenly spaced, they are moved but any bound arrows remain in their old positions.

2. **Text container resizing** - When text overflows or shrinks inside a container in WYSIWYG mode, the container height changes but bound arrows are not repositioned.

## Expected Behavior

After the fix, bound arrows should remain correctly attached to their target elements after both distribution operations and text container resizing operations.

The fix involves calling `updateBoundElements` at appropriate points in both code paths. The function is already available in the codebase.

## Implementation Requirements

### Distribution Code Path

- The `distributeElements` function (in `packages/element/src/distribute.ts`) must accept a `Scene` parameter as part of its signature.
- The action in `packages/excalidraw/actions/actionDistribute.tsx` must pass the Scene object to `distributeElements` when calling it.

### WYSIWYG Code Path

- The `textWysiwyg.tsx` file (in `packages/excalidraw/wysiwyg/`) must import the `updateBoundElements` function.
- After mutating a text container's height, the code must call `updateBoundElements` on that container.