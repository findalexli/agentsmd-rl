# DevTools Owners Breadcrumbs Overflow Issue

In the React DevTools, there's a component that displays the "Owners" breadcrumbs in a component tree view. This component needs to detect when its content overflows the available width so it can show a shrunken/shrinkable version.

## Problem

The current overflow detection only triggers when the browser window is resized. However, this misses an important case: **when inner panes within the DevTools are resized** (for example, dragging the sidebar divider), the available width for the breadcrumbs changes, but the overflow detection doesn't fire.

This causes the breadcrumbs to:
1. Take up all available space even when they shouldn't
2. Prevent proper pane resizing with custom resize handles
3. Show overflowed content momentarily before detecting the actual state

## Where to look

The relevant hook is in `packages/react-devtools-shared/src/devtools/views/hooks.js` — specifically the `useIsOverflowing` hook.

## Expected behavior

The overflow state should update whenever the container's dimensions change, including:
- Browser window resize (already works)
- Pane/divider resize within DevTools UI (currently broken)

This should work correctly in both the standalone DevTools and the browser extension (note that the extension uses portals, so elements may be in different documents/windows).

## Notes

- The hook currently uses a `useLayoutEffect` to avoid flashing overflowed content — this timing consideration should be preserved.
- The solution needs to handle the browser extension case where elements may be rendered in portals with different owner documents.
