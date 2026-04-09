# Fix Arrow Overlap Arrow Behavior

## Problem

When an arrow connects two elements that overlap (or when the arrow itself becomes very short due to element positioning), the arrow can exhibit incorrect behavior:

1. **Arrow inversion**: The arrow may flip or invert when it shouldn't
2. **Incorrect endpoint positioning**: Arrow endpoints don't correctly snap to element outlines when elements overlap
3. **"Dancing" arrows**: Arrows may jitter or change position unexpectedly during drag operations
4. **Stale state during projection**: When projecting fixed points onto diagonals during element movement, the arrow can use stale state causing incorrect positioning

## Affected Files

The arrow binding system involves these key files:

- **`packages/element/src/binding.ts`** - Core arrow binding logic, particularly `updateBoundPoint` function
- **`packages/element/src/utils.ts`** - `projectFixedPointOntoDiagonal` function for fixed point projections
- **`packages/element/src/linearElementEditor.ts`** - Arrow endpoint dragging logic
- **`packages/element/src/align.ts`** - Element alignment that affects bound arrows
- **`packages/element/src/arrows/focus.ts`** - Arrow focus point calculations
- **`packages/excalidraw/components/App.tsx`** - App-level binding updates

## Key Functions to Modify

1. **`updateBoundPoint`** - The main function that calculates where an arrow endpoint should be positioned when bound to an element. Currently accepts a `customIntersector` option that should be replaced with a simpler `dragging` boolean parameter.

2. **`projectFixedPointOntoDiagonal`** - Should use the opposite focus point to avoid stale state when moving arrow endpoints.

3. **`updateBoundElements`** - Currently has an `indirectArrowUpdate` option that causes redundant updates and should be removed.

## Expected Behavior

After the fix:

- Arrows should maintain proper orientation when connecting overlapping elements
- Arrow endpoints should correctly snap to element outlines based on the arrow's length and binding mode
- During element movement, arrow calculations should use consistent focus points to avoid stale state issues
- The `updateBoundPoint` function should have a cleaner interface without the `customIntersector` complexity

## Guidelines

- Follow the existing TypeScript patterns in the codebase
- Maintain type safety throughout the changes
- The fix involves removing the `indirectArrowUpdate` option from `updateBoundElements` and simplifying the `updateBoundPoint` signature
- Run `yarn test:typecheck` and `yarn test:update` to verify your changes
