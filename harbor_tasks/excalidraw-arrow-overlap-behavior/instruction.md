# Fix Arrow Overlap Behavior

## Problem

When arrows bind to elements that overlap or are very close together, the arrow endpoints behave incorrectly. Arrows may invert direction, jump around, or display at incorrect positions when:

1. Two elements with bound arrows overlap each other
2. An arrow becomes too short (less than ~10 pixels between elements)
3. Elements are dragged close to each other while maintaining arrow bindings

The root cause is that the current `updateBoundPoint` logic does not properly handle the case where elements overlap, and the `indirectArrowUpdate` option in `updateBoundElements` introduces incorrect behavior when elements are moved programmatically (e.g., via alignment operations). The `customIntersector`-based approach in `linearElementEditor.ts` also contributes to the problem.

## Relevant Files

- `packages/element/src/binding.ts` - Core binding logic including `updateBoundPoint` and `updateBoundElements`
- `packages/element/src/linearElementEditor.ts` - Arrow editor logic for dragging
- `packages/element/src/arrows/focus.ts` - Focus point handling for arrow bindings
- `packages/element/src/utils.ts` - Utility functions for element calculations
- `packages/element/src/align.ts` - Alignment operations that move elements programmatically
- `packages/excalidraw/components/App.tsx` - Main application component

## Expected Behavior

After fixing, the arrow binding system should satisfy the following:

### binding.ts

- A constant `BASE_ARROW_MIN_LENGTH` set to `10` should be defined, establishing the threshold below which arrows are considered too short and should use focus points rather than outline points
- The `updateBoundPoint` function should accept a `dragging?: boolean` parameter instead of the current options object with `customIntersector`
- The `updateBoundElements` function should not have the `indirectArrowUpdate?: boolean` option
- Helper functions `extractBinding` and `elementArea` should be present for cleaner code organization
- A `pointIsCloseToOtherElement` check should be used to determine when outline points are near other bound elements
- Unused imports from `./bounds` — specifically `doBoundsIntersect` and `getElementBounds` — should be removed

### linearElementEditor.ts

- The `customIntersector` approach should be replaced; `endIsDragged` and `startIsDragged` flags should be passed as the dragging parameter to `updateBoundPoint`

### focus.ts

- Calls to `updateBoundPoint` should pass `true` as the dragging parameter

### utils.ts

- Should import `getGlobalFixedPointForBindableElement` and `normalizeFixedPoint` from the arrows module
- For two-point arrows, the opposite element's focus point should be used, with a comment noting "To avoid working with stale arrow state"

### align.ts and App.tsx

- The `indirectArrowUpdate: true` option should be removed from all `updateBoundElements` calls

## Agent Config Notes

From the repo's agent configs:
- Use TypeScript for all new code with proper typing
- Use immutable data (const, readonly) where applicable
- Prefer modern TypeScript operators (?., ??)
- Run `yarn test:typecheck` to verify TypeScript
- Run tests before committing
