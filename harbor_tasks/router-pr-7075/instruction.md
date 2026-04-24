# Bug: Child route handlers execute after parent beforeLoad fails during preload

## Problem

When using TanStack Router's preload functionality with nested routes, there's a bug where child route handlers continue executing even after a parent route's `beforeLoad` handler throws an error during preload.

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

## Root Cause

The preload loop in `packages/router-core/src/load-matches.ts` does not properly stop when encountering a match that has failed its beforeLoad hook. When a parent match's beforeLoad fails, subsequent child matches in the chain are still being processed and their handlers are being invoked. An error boundary tracking field (which match first failed) is not being properly consulted when deciding whether to continue processing subsequent matches or invoke their handlers.

Specifically, when a beforeLoad throws during preload, child route handlers continue to execute. The fix requires tracking the index of the first match that encounters an error (`firstBadMatchIndex`) and using it to prevent further handler invocation. The `headMaxIndex` value used to limit head handler execution must be derived from this error boundary, not from the default last-match calculation.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
