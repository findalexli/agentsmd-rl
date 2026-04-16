# Fix deepEqual function to handle promise-like objects

The `deepEqual` function in `packages/solid-router/src/useRouterState.tsx` doesn't correctly handle promise-like objects.

## Problem

When comparing two different promise objects or thenable values (objects with a `.then` method), `deepEqual` tries to recursively compare their properties. This leads to incorrect behavior - two different promises that resolve to the same value might be incorrectly considered equal, or the comparison might fail unexpectedly.

## Expected behavior

- Two different promise objects should NOT be considered deeply equal (unless they are the same reference)
- Thenable objects (any object with a `.then` method) should be treated as promise-like
- Comparing a promise to a regular object should return `false`
- Regular (non-promise) object comparison should continue to work as before

## Location

The `deepEqual` function is defined in `packages/solid-router/src/useRouterState.tsx`. It is used internally to compare router state values.

## Hints

- Promise-like values can be detected by checking if they have a `.then` method that is a function
- Consider handling both native Promises and custom thenable objects
- The fix should be early in the comparison logic to avoid trying to iterate over promise properties
