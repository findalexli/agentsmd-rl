# Bug Report: Suspense tab breadcrumbs overflow outside container when deeply nested

## Problem

In the React DevTools Suspense tab, when navigating into deeply nested Suspense boundaries, the breadcrumb trail grows unbounded horizontally. The breadcrumb list has no overflow handling, so as more items are added, they extend beyond the visible area of the panel. There is no mechanism to collapse or truncate the breadcrumb trail when it exceeds the available width.

## Expected Behavior

When the breadcrumb trail exceeds the available horizontal space, it should gracefully handle overflow — for example, by collapsing earlier breadcrumb items into a dropdown menu so the current location remains visible and the UI stays within its container bounds.

## Actual Behavior

The breadcrumb list renders all items in a single non-wrapping flex row with no overflow management. As the user navigates deeper into the Suspense tree, breadcrumbs push content off-screen or cause unwanted horizontal scrolling within the DevTools panel.

## Files to Look At

- `packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseBreadcrumbs.css`
- `packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseBreadcrumbs.js`
- `packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.css`
- `packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.js`
