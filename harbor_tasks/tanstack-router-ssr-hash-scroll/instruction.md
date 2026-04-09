# Fix SSR Hash Scroll Preservation Bug

## Problem

TanStack Router has a bug where the scroll position anchored to a URL hash (e.g., `/page#section`) gets reset after SSR hydration when:
1. Preloading another route via hover
2. Invalidating router data

The symptom is that after the page loads with a hash URL and the browser scrolls to the target element, any subsequent preload or invalidation causes the page to scroll back to the hash target, losing the user's current scroll position.

## Location

The bug is in `packages/router-core/src/ssr/ssr-client.ts` in the `hydrate()` function.

## Root Cause

During SSR hydration, `router.load()` is skipped (because the server already loaded the data). This leaves `router.stores.resolvedLocation` as `undefined`. Later, when a preload or invalidation triggers a load cycle, the router incorrectly detects a location change (undefined → current location) and re-runs hash scrolling.

## Required Fix

After SSR hydration completes, set `router.stores.resolvedLocation` to the current location state. This prevents subsequent load cycles from mistakenly detecting a location change.

The fix should be added after the line that clears the dehydrated flag in the hydrate function, and should include a comment explaining why it's needed.

## Testing

After applying the fix:
1. The TypeScript should compile without errors
2. The router-core package should build successfully
3. Unit tests should still pass

## Agent Rules

- Use `pnpm nx run @tanstack/router-core:build` to build the package
- Use `pnpm nx run @tanstack/router-core:test:unit` for unit tests
- If Nx commands hang, try `CI=1 NX_DAEMON=false pnpm nx ... --skipRemoteCache`
