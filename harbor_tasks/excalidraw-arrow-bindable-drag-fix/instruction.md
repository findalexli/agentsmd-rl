# Fix Arrow Drag Behavior in Bindable Areas

## Problem

When a user starts dragging an arrow from within a bindable element's area (like a rectangle), the arrow "jumps" across the element instead of starting from the correct position under the cursor.

## Relevant Files

- `packages/element/src/binding.ts`

## Details

When an arrow is first created via pointer-down, its last point is initialized at the origin `[0, 0]` as a placeholder. The bound-point update logic in this file doesn't account for this initial state — it updates the arrow's points even during the creation phase, causing the observed "jump" behavior.

The fix should detect when the arrow is still in its initial state (i.e., its last point equals the origin) and return early without modifying the points.

The codebase provides a `pointsEqual` utility in the `@excalidraw/math` package for comparing point values, and `pointFrom<LocalPoint>(0, 0)` for constructing the origin point. The added check should be accompanied by the comment:

```
// Initial arrow created on pointer down needs to not update the points
```

## Expected Behavior

After the fix:
- Starting to drag an arrow from within a bindable element should begin at the cursor position
- The arrow should not "jump" across the element
- Existing tests should continue to pass
