# Scroll Position Not Restored on Browser Forward Navigation

## Problem

When using TanStack Router's scroll restoration feature, navigating forward in browser history (using the browser's forward button) fails to restore the previous scroll position. The scroll position is correctly saved when leaving a page, but when navigating back and then forward, the page scrolls to the top instead of the previously saved position.

## Relevant Code

The scroll restoration logic is in:
- `packages/router-core/src/scroll-restoration.ts`

The `setupScrollRestoration` function manages saving and restoring scroll positions based on navigation events.

This module must export:
- `export function setupScrollRestoration`
- `export const scrollRestorationCache`
- `export const defaultGetScrollRestorationKey`

The module sets up these event subscriptions:
- `router.subscribe('onBeforeLoad', ...)` - for handling scroll snapshots before navigation
- `router.subscribe('onRendered', ...)` - for restoring scroll position after render
- `document.addEventListener('scroll', ...)` - for tracking scroll position changes
- `window.addEventListener('pagehide', ...)` - for persisting scroll state on page hide

The scroll cache is initialized in the `onRendered` handler with this pattern:
- `cache.set((state) => { state[cacheKey] ||= ... })`

## Steps to Reproduce

1. Navigate to a page with scroll restoration enabled
2. Scroll down on the page
3. Navigate to another page (via link click)
4. Click browser back button - scroll position is correctly restored
5. Click browser forward button - **scroll position is NOT restored** (bug)

## Expected Behavior

After pressing the browser forward button, the page should restore to the scroll position that was saved when the user originally left that page.

The `onRendered` event handler should not contain any logic that clears the scroll restoration cache based on navigation direction. The cache should be preserved so that scroll positions can be restored on both backward and forward navigation.

## Actual Behavior

The scroll position is lost on forward navigation. The page resets to the top because the scroll cache is incorrectly cleared before restoration can occur.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
