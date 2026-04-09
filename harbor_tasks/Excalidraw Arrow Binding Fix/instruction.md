# Fix Arrow Drag Start Jumping in Bindable Areas

## Problem Description

When dragging an arrow that starts within a bindable element's area (like a rectangle or shape), the arrow unexpectedly jumps across the bindable element instead of starting from the correct position. This creates a jarring user experience where the arrow doesn't follow the cursor naturally during initial drag operations.

## Reproduction Steps

1. Create a bindable element (e.g., a rectangle)
2. Start dragging an arrow from within the bindable element's area
3. Observe that the arrow jumps unexpectedly instead of following the cursor smoothly

## Expected Behavior

When starting to drag an arrow from within a bindable element's area, the arrow should:
- Not update its points during the initial creation phase
- Start from the correct position near the cursor
- Not jump across the bindable element

## Relevant Code

The issue is in the arrow binding logic. Look at:
- `packages/element/src/binding.ts` - specifically the `updateBoundPoint` function
- The function handles updating arrow points when interacting with bindable elements
- The fix needs to detect when an arrow is in its initial creation state and prevent premature point updates

## Hints

- The arrow has a `points` array that contains its coordinates
- During initial creation, the arrow's last point is at a specific default position
- The fix should add a check to detect this initial state and skip updating points
- You'll need to import a utility function from the math package to compare points

## Success Criteria

1. TypeScript compiles without errors
2. The fix properly detects initial arrow creation and prevents point updates
3. Existing unit tests related to arrow movement and binding pass
4. The code follows the project's patterns (immutability, performance considerations)
