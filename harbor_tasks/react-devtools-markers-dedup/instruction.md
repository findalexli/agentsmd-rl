# React DevTools: Suspense Boundary Unique Suspenders Tracking Bug

## Problem

The React DevTools backend has a bug in how it tracks `uniqueSuspenders` for nested Suspense boundaries. When a Suspense boundary has multiple child components suspended on the same I/O (promise), and only some (but not all) of those children are removed, inner Suspense boundaries may incorrectly be marked as having unique suspenders even though they are still blocked by the parent boundary.

## Location

File: `packages/react-devtools-shared/src/backend/fiber/renderer.js`

Look for the `unblockSuspendedBy` function and its call sites within the suspense node update logic.

## Expected Behavior

When a Suspense boundary has multiple children suspended on the same promise/I/O:
1. The boundary should only be considered "unblocked" from that I/O when **all** children blocking on that I/O are removed
2. Child Suspense boundaries should continue to show `uniqueSuspenders: false` as long as they are still blocked by an ancestor boundary that is itself blocked on the same I/O
3. Only when the parent boundary truly has no more children blocking on that I/O should the child boundaries be re-evaluated for unique suspender status

## What to Look For

The bug is in the logic that determines when to call `unblockSuspendedBy`. Currently, this may be triggered when **any** child with the I/O is removed, rather than only when **all** children with that I/O are removed. The fix should ensure the unblocking logic only runs when the suspender count actually reaches zero.

## Test Hint

The existing test suite in `packages/react-devtools-shared/src/__tests__/store-test.js` has tests for Suspense boundary tracking. Look for tests involving `uniqueSuspenders` and use them to understand the expected behavior and verify your fix.
