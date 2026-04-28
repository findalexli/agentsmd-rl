# Fix Arrow Drag Start Jumping in Bindable Areas

## Problem Description

When creating an arrow by dragging from within a bindable element's area (such as a rectangle), the arrow unexpectedly jumps across the element instead of starting from the correct position near the cursor. This is a visual glitch that occurs specifically during the initial creation phase of the arrow — the binding endpoint update logic doesn't account for the initial arrow state, causing the premature jump.

## Reproduction Steps

1. Create a bindable element (e.g., a rectangle)
2. Start dragging to create an arrow from within the bindable element's area
3. Observe that the arrow jumps unexpectedly instead of following the cursor smoothly

## Technical Context

Arrows have a `points` array (`arrow.points`) that tracks their coordinates. During the initial creation phase, the arrow's last point starts at the origin `(0, 0)`. The arrow's `points` array can be inspected to detect this initial creation state.

The arrow binding logic in `packages/element/src/binding.ts` handles endpoint updates during binding interactions. The existing code contains these patterns which must all be preserved in the fix:
- `binding == null` — early return for unbound arrows
- `elementId !== bindableElement.id` — element identity check
- `arrow.points.length > 2` — multi-point arrow check

The `packages/math` package provides point utilities including `pointsEqual` (for comparing whether two points are equal) and `pointFrom` (for constructing typed points). These may be useful for the fix.

## Expected Behavior

- The arrow should follow the cursor naturally during creation from within a bindable element
- All existing binding logic and code patterns must be preserved

## Success Criteria

1. TypeScript compiles without errors: `yarn test:typecheck`
2. Move tests with binding pass: `yarn test:app move.test.tsx -t "rectangles with binding arrow" --run`
3. History tests with binding pass: `yarn test:app history.test.tsx -t "bidirectional binding" --run`
4. ESLint passes: `yarn test:code`
5. Prettier passes: `yarn test:other`
6. Element package tests pass: `yarn test:app --run packages/element`
7. Math package tests pass: `yarn test:app --run packages/math`
8. Common package tests pass: `yarn test:app --run packages/common`
9. Utils package tests pass: `yarn test:app --run packages/utils`
10. Binding tests pass: `yarn test:app --run packages/element/tests/binding.test.tsx`
