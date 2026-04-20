# Fix ScrollArea overscroll-behavior CSS variable for directional scrollbars

## Context

The Mantine `ScrollArea` component supports an `overscrollBehavior` prop that maps to the CSS `overscroll-behavior` property. It also supports a `scrollbars` prop with values `'x'`, `'y'`, `'xy'`, or `false` to control which scrollbars are rendered.

The CSS `overscroll-behavior` property accepts one or two values:
- A single value applies to both axes (e.g., `overscroll-behavior: contain`)
- Two values apply to x-axis and y-axis respectively (e.g., `overscroll-behavior: contain auto` means x-axis uses `contain`, y-axis uses `auto`)

## Problem

When `scrollbars` is set to `'x'` or `'y'`, the `--scrollarea-over-scroll-behavior` CSS variable still receives a single value from the `overscrollBehavior` prop. This means the overscroll behavior is applied to **both** axes even though only one axis has a visible scrollbar.

For example, with `scrollbars="x"` and `overscrollBehavior="contain"`, the CSS variable is set to `contain` — which prevents overscroll on **both** the x-axis and y-axis. Since there is no y-axis scrollbar, the y-axis overscroll behavior should remain `auto` (the browser default), producing `contain auto`.

Similarly, with `scrollbars="y"` and `overscrollBehavior="contain"`, the expected value is `auto contain`.

The `overscroll-behavior` CSS property is defined in the component's `varsResolver` function, which computes CSS custom properties from component props. The resolver is created using Mantine's `createVarsResolver` utility and receives the component props (including `scrollbars` and `overscrollBehavior`).

## Expected behavior

- When `scrollbars` is `'x'` and `overscrollBehavior` is set, `--scrollarea-over-scroll-behavior` should be `"<value> auto"` (e.g., `"contain auto"`, `"none auto"`)
- When `scrollbars` is `'y'` and `overscrollBehavior` is set, `--scrollarea-over-scroll-behavior` should be `"auto <value>"` (e.g., `"auto contain"`, `"auto none"`)
- When `scrollbars` is `'xy'` (the default) or not set, the behavior should remain unchanged (single value)
- When `overscrollBehavior` is not provided, the CSS variable should not be set

## Relevant files

- `packages/@mantine/core/src/components/ScrollArea/ScrollArea.tsx` — contains the `varsResolver` function that computes the CSS variable
