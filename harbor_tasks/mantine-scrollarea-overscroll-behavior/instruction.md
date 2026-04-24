# Fix ScrollArea overscroll-behavior for single-axis scrollbars

## Problem

When a `ScrollArea` with `scrollbars="x"` (horizontal-only) is nested inside a vertically scrollable container, vertical wheel events are captured and do not propagate to the parent. This breaks the expected scrolling behavior.

Similarly, when `scrollbars="y"` (vertical-only), horizontal scroll events should not be consumed.

The issue is in the Mantine core package's ScrollArea component. The CSS variable resolver that computes style variables from component props does not account for the `scrollbars` prop when setting the `overscroll-behavior` CSS variable.

## Expected Behavior

The resolver must be updated to handle single-axis scrollbar configurations. The implementation should satisfy the following requirements:

- The resolver function signature must destructure `scrollbarSize`, `overscrollBehavior`, and `scrollbars` (in that order) from the props, and use a function body with curly braces rather than a concise arrow expression:
  `(_, { scrollbarSize, overscrollBehavior, scrollbars }) => { ... }`

- Declare a local variable named `overrideOverscrollBehavior`, initialized to the value of `overscrollBehavior`.

- Guard the axis-specific logic with: `if (overscrollBehavior && scrollbars)`

- Inside the guard:
  - `if (scrollbars === 'x')`: set `overrideOverscrollBehavior` to `` `${overscrollBehavior} auto` ``
  - `else if (scrollbars === 'y')`: set `overrideOverscrollBehavior` to `` `auto ${overscrollBehavior}` ``

- Use `overrideOverscrollBehavior` as the value for the `--overscroll-behavior`-related CSS variable in the returned style object.

- When `scrollbars="xy"` or when scrollbars is not set, the existing behavior should be preserved (the guard condition naturally handles this).

## CSS Background

The `overscroll-behavior` CSS property controls what happens when you reach the boundary of a scrollable area. The two-value syntax is:
- `overscroll-behavior: x-behavior y-behavior`

Setting one axis to `auto` allows scroll events to propagate to the parent container for that axis.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
- `stylelint (CSS linter)`
