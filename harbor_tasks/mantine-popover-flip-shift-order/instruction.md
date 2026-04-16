# Fix Popover Middleware Order

## Problem

When a Popover or Menu is positioned at the edge of the screen, its floating element overlaps with its trigger instead of flipping to the opposite side. This is caused by incorrect middleware ordering in the Popover positioning logic.

## Affected File

`packages/@mantine/core/src/components/Popover/use-popover.ts`

## Context

The `getPopoverMiddlewares()` function in this file builds an array of floating-ui middlewares that control positioning behavior. The order in which middlewares are added to this array determines their execution order, which directly affects how the popover is positioned.

The middlewares involved are:
- `offset` — adds spacing between reference and floating element
- `hide` — hides the floating element when it escapes reference
- `shift` — pushes the element to stay within viewport, using `limitShift()` with `padding: 5`
- `flip` — flips the element to opposite placement if needed, accepting either a boolean or object via `middlewaresOptions.flip`

## Bug Description

Currently, when the `shift` middleware executes before `flip`, it pushes the popover into the viewport first. This prevents `flip` from detecting an overflow condition, so `flip` never triggers and the popover ends up overlapping its trigger at screen edges instead of repositioning to the opposite side.

According to the [floating-ui documentation on combining flip with shift](https://floating-ui.com/docs/flip#combining-withshift), the interaction between these two middlewares is sensitive to ordering. Review the documentation to understand the recommended middleware execution order when using both `flip` and `shift` together.

## Requirements

- The fix must preserve the existing implementation of both the `shift` and `flip` middleware blocks (including `limitShift()`, `padding: 5`, and the conditional boolean/object logic for `flip()`)
- The file must pass ESLint, TypeScript type checking, and Prettier formatting
- All existing Popover tests must continue to pass
