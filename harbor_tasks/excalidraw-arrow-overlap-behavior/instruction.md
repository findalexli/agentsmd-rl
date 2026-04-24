# Fix Arrow Overlap Behavior

## Problem

When arrows bind to elements that overlap or are very close together, the arrow endpoints behave incorrectly. Arrows may invert direction, jump around, or display at incorrect positions when:

1. Two elements with bound arrows overlap each other
2. An arrow becomes too short (less than approximately 10 pixels between elements)
3. Elements are dragged close to each other while maintaining arrow bindings

The current `updateBoundPoint` logic does not properly handle overlapping elements, and the `indirectArrowUpdate` option in `updateBoundElements` introduces incorrect behavior when elements are moved programmatically (e.g., during alignment operations). Additionally, the approach using `customIntersector` in `linearElementEditor.ts` contributes to endpoint positioning issues.

## Relevant Files

- `packages/element/src/binding.ts` - Core binding logic including `updateBoundPoint` and `updateBoundElements`
- `packages/element/src/linearElementEditor.ts` - Arrow editor logic for dragging
- `packages/element/src/arrows/focus.ts` - Focus point handling for arrow bindings
- `packages/element/src/utils.ts` - Utility functions for element calculations
- `packages/element/src/align.ts` - Alignment operations that move elements programmatically
- `packages/excalidraw/components/App.tsx` - Main application component

## Expected Behavior

After fixing, the arrow binding system should satisfy the following:

### Arrow behavior with overlapping/close elements

- A minimum arrow length constant should be defined in `binding.ts` — use a descriptive name (e.g., `BASE_ARROW_MIN_LENGTH`) to distinguish it from any other length constants
- Arrows should use focus points instead of outline points when they become too short (less than ~10 pixels between elements)
- When outline points would place the arrow near another bound element, the system should detect this and avoid arrow inversion
- The binding system should properly handle the case where elements overlap

### updateBoundPoint interface

- The `updateBoundPoint` function signature should be simplified — replace the `opts?: { customIntersector?: ... }` parameter with a simpler `dragging?: boolean` parameter
- When an endpoint is being actively dragged, this should be communicated via the `dragging` parameter so the function can decide which points to use
- The `indirectArrowUpdate?: boolean` option should be removed from `updateBoundElements` — it causes incorrect behavior when elements are moved programmatically

### Arrow dragging in linearElementEditor

- When dragging arrow endpoints, the system should track which specific endpoint is being moved using flags like `endIsDragged` and `startIsDragged` passed to `updateBoundPoint`
- The custom intersector approach (`customIntersector`) should be removed from `linearElementEditor.ts`

### Focus point handling

- Focus point calculations should use stable reference points that don't become stale during drag operations
- The `utils.ts` file should import and use `getGlobalFixedPointForBindableElement` and `normalizeFixedPoint` for focus point calculations
- For two-point arrows, using the opposite element's focus point helps avoid inconsistencies

### align.ts and App.tsx

- Remove any `indirectArrowUpdate: true` option from all `updateBoundElements` calls in `align.ts` and `App.tsx` — this option causes issues during programmatic element movement
- The `binding.ts` file should not import `doBoundsIntersect` or `getElementBounds` from `./bounds` (any unused bounds functions should be cleaned up)

## Agent Config Notes

From the repo's agent configs:
- Use TypeScript for all new code with proper typing
- Use immutable data (const, readonly) where applicable
- Prefer modern TypeScript operators (?., ??)
- Run `yarn test:typecheck` to verify TypeScript
- Run tests before committing
