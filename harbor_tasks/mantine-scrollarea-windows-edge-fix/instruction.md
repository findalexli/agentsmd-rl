# Fix Windows Edge Horizontal Scroll Propagation in Mantine ScrollArea

## Bug Report

In the Mantine UI library, the `ScrollArea` component has a scroll propagation bug that affects Windows Edge users. When horizontal scrolling is enabled and the viewport is scrolled to its top or bottom vertical boundary, pressing Shift+scroll wheel to scroll horizontally causes the parent element or page to scroll instead of allowing horizontal scrolling within the container.

The affected component is `ScrollAreaViewport` in the `@mantine/core` package at `packages/@mantine/core/src/components/ScrollArea/ScrollAreaViewport/ScrollAreaViewport.tsx`. Currently, this component does not handle wheel events at all, so it cannot intercept the problematic browser scroll propagation.

## Component Context

The `ScrollAreaViewport` component is a `forwardRef` component that renders a `Box` element. It uses:

- `useScrollAreaContext()` — provides `scrollbarXEnabled` (boolean for whether horizontal scrollbar is enabled), `viewport` (reference to the viewport DOM element), and `onViewportChange`
- `useMergedRef` — for combining the forwarded ref with the context's viewport ref

The component currently accepts `children`, `style`, and spreads remaining props onto `Box`.

## Expected Behavior After Fix

The component should intercept wheel events on the `Box` element to prevent scroll propagation to parent elements when all of the following conditions are true:

- Horizontal scrolling is enabled (`ctx.scrollbarXEnabled` is truthy) and a viewport element exists (`ctx.viewport`)
- The user is holding the Shift key (`event.shiftKey`), indicating horizontal scroll intent
- The viewport is at a vertical scroll boundary — either at the top (where `scrollTop < 1`) or at the bottom (where `scrollTop >= scrollHeight - clientHeight - 1`)
- The content can actually scroll horizontally (`scrollWidth > clientWidth`)

When these conditions are met, the event should be stopped from propagating via `event.stopPropagation()`. Any user-provided `onWheel` handler must still be invoked.

## Acceptance Criteria

The fix must conform to the following conventions used in this codebase:

- Extract `onWheel` from the component's props so it can be forwarded
- Define a wheel event handler as `const handleWheel = (event:` with the appropriate React type
- Forward the user's handler using optional chaining: `onWheel?.(event)`
- Attach the handler to the Box element: `onWheel={handleWheel}`
- Name the boundary detection variables `isAtTop`, `isAtBottom`, and `canScrollHorizontally`
- The condition checking horizontal scroll eligibility must include `ctx.scrollbarXEnabled`, `ctx.viewport`, and `event.shiftKey`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
