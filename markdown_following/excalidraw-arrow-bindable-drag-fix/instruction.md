# Fix Arrow Drag Behavior in Bindable Areas

## Problem

When a user starts dragging an arrow from within a bindable element's area (like a rectangle), the arrow "jumps" across the element instead of starting from the correct position under the cursor. This makes it difficult to precisely place arrow endpoints when they need to land inside or near other shapes.

## Details

Excalidraw supports binding arrows to other elements (rectangles, diamonds, ellipses, etc.) so that arrows stay attached when the bound element is moved. Each arrow is a linear element with an array of points defining its path.

When an arrow is first created via pointer-down, its last point is initialized at the origin `[0, 0]` as a placeholder. This is a temporary value set before the user finishes the drag gesture. The bound-point update logic doesn't account for this initial state — it updates the arrow's points even during the creation phase, causing the observed "jump" behavior. Instead of starting at the cursor, the arrow endpoint snaps across the bindable element.

The fix should detect when the arrow is still in its initial state (i.e., its last point equals the origin) and return early without modifying the points. This allows the arrow to begin at the actual cursor position.

## Expected Behavior

After the fix:
- Starting to drag an arrow from within a bindable element should begin at the cursor position
- The arrow should not "jump" across the element
- Arrow binding to elements during normal editing (not initial creation) must continue to work
- Existing tests should continue to pass

## Project Setup

This is a Yarn workspaces monorepo. The codebase is TypeScript with Jest/Vitest for testing. Key packages:
- `packages/element/` — Element types, collision detection, and binding logic
- `packages/excalidraw/` — Main application package with UI and tests

## Running Tests

- Type checking: `yarn test:typecheck`
- Linting (ESLint): `yarn test:code`
- Formatting (Prettier): `yarn test:other`
- Application tests: `yarn test:app [test-file-path]` (runs vitest)

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
