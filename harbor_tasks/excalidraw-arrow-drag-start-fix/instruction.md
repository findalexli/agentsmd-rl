# Fix Arrow Drag Start Jumping in Bindable Area

## Problem

When users drag to create an arrow starting from within a bindable element's area (like a rectangle), the arrow incorrectly jumps across the element instead of starting from the pointer position. This causes a confusing user experience where the arrow appears to "snap" to the wrong location immediately on pointer down.

## Relevant Code

The issue is in `packages/element/src/binding.ts` in the `updateBoundPoint` function. This function is responsible for updating arrow binding points when elements move or when arrows are being created.

## Symptoms

1. Start dragging to create an arrow from within a rectangle
2. The arrow immediately jumps to an incorrect position instead of starting from where the pointer is
3. The arrow end point gets incorrectly bound during the initial creation phase

## Expected Behavior

When an arrow is first being created (pointer down), the `updateBoundPoint` function should recognize this initial state and skip the binding update. The arrow should start from the pointer position, not jump to a calculated binding point.

## Agent Configuration Notes

From CLAUDE.md:
- This is a monorepo with packages in `packages/`
- Use `yarn test:typecheck` for TypeScript validation
- Run `yarn test:update` before committing

From .github/copilot-instructions.md:
- Include `packages/math/src/types.ts` when writing math-related code
- Use the Point type instead of `{x, y}`
- Prefer implementations without allocation
- Trade RAM usage for fewer CPU cycles where possible

## Files to Modify

- `packages/element/src/binding.ts` - Add logic to detect initial arrow state and skip binding updates

## Hints

The key insight is distinguishing between:
1. An arrow being created (initial state) - should not update binding
2. An arrow being modified after creation - should update binding normally

Look for a way to detect the initial arrow state by examining the arrow's points. The last point position can indicate whether the arrow is still in its initial creation state.
