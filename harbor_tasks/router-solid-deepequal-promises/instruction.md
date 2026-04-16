# Fix deepEqual Promise Handling in Solid Router

## Problem

The `deepEqual` function in `packages/solid-router/src/useRouterState.tsx` has a bug when comparing Promise-like objects. When two different Promises (or objects with a `.then` method) are compared, the function may incorrectly return `true` instead of `false`, treating them as equal when they are not.

This can cause issues with router state management where Promises representing async data should be treated as distinct values, not deep-compared as regular objects.

## Symptoms

- Comparing two different Promise objects returns `true` instead of `false`
- Objects containing Promises are incorrectly considered equal even when containing different Promise instances
- Thenable objects (objects with `.then` method) are deep-compared instead of being recognized as Promise-like

## Relevant Code

The `deepEqual` function is located in `packages/solid-router/src/useRouterState.tsx` and is used by `useRouterState` to compare selected state values.

## Expected Behavior

- `deepEqual(promise1, promise2)` should return `false` when `promise1 !== promise2`
- `deepEqual(promise, regularObject)` should return `false`
- `deepEqual(samePromise, samePromise)` should return `true` (same reference)
- `deepEqual({ data: promise1 }, { data: promise2 })` should return `false` for different promises

## Notes

- This is a TypeScript project using pnpm and Nx for task management
- The fix should handle all Promise-like objects (anything with a `.then` method)
- Run tests using `pnpm nx run @tanstack/solid-router:test:unit`
- Build with `pnpm nx run @tanstack/solid-router:build`
