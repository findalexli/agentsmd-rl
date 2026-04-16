# Bug: Child route handlers execute after parent beforeLoad fails during preload

## Problem

When using TanStack Router's preload functionality with nested routes, there's a bug where child route handlers continue executing even after a parent route's `beforeLoad` handler throws an error during preload.

The bug is in the preload loop implementation in `packages/router-core/src/load-matches.ts`.

## Expected Behavior

When a parent route's `beforeLoad` handler throws an error during preloading:
1. The preload operation should stop immediately
2. Child routes' `beforeLoad` handlers should NOT be called
3. Child routes' `head` handlers should NOT be called

## Actual Behavior

Currently, even when a parent route's `beforeLoad` throws during preload:
- Child routes' `beforeLoad` handlers are still being called
- Child routes' `head` handlers are still being called

This is incorrect because the child routes depend on the parent route loading successfully.

## Reproduction

Create a router with nested routes where:
- Parent route has a `beforeLoad` that throws when `preload` is true
- Child route has `beforeLoad` and `head` handlers

Call `router.preloadRoute({ to: '/parent/child' })` and observe that the child handlers are invoked even though the parent failed.

## Implementation Notes

The fix must properly track the position of errors in the route match chain to determine which handlers should execute. The preload loop needs to respect error boundaries - when a match in the chain encounters an error, subsequent child matches in that chain should not have their handlers invoked.

Specifically:

1. **Loop termination condition**: The preload loop's break condition must check for both the existing error state AND whether any match (including the current one) has failed, stopping processing when an error boundary is reached.

2. **Head handler limit**: The calculation that determines which matches get their head handlers invoked must properly account for where in the match chain an error occurred, ensuring head handlers only run for matches up to and including the first failed match, not for subsequent child matches.

The fix requires tracking which match index first encounters an error, and the loop must respect this boundary when deciding which matches to process further.
