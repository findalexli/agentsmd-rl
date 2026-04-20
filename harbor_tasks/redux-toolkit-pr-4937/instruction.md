# Task: Fix Referential Stability in useInfiniteQuerySubscription

## Problem Description

The `useInfiniteQuerySubscription` hook in `@reduxjs/toolkit/query/react` has referential stability issues with its return value.

### Symptoms

When using infinite queries, the `fetchNextPage`, `fetchPreviousPage`, and `refetch` functions returned by the hook are not referentially stable. This means:

1. **Unnecessary re-renders**: Components that receive these functions as props or depend on them via `useCallback`/`useMemo` will re-render even when the underlying query data hasn't changed.

2. **Broken memoization**: Custom hooks that rely on referential equality checks (e.g., `useCallback(() => data.fetchNextPage, [data.fetchNextPage])`) will treat the function as changed on every render, defeating the purpose of memoization.

3. **Infinite loops**: In some cases, unstable function references can cause infinite render loops when used as dependency arrays for other hooks.

### Affected Hook

- `useInfiniteQuerySubscription` (from `@reduxjs/toolkit/query/react`)
- Returns: `{ fetchNextPage, fetchPreviousPage, refetch, trigger }`

### Required Implementation

To fix the referential stability, the following patterns must appear in `packages/toolkit/src/query/react/buildHooks.ts`:

1. **refetch stability**: The `refetch` function must be wrapped in `useCallback`:
   ```
   const refetch = useCallback(..., [...])
   ```
   It must call `refetchOrErrorIfUnmounted(promiseRef)`.

2. **Pagination argument stability**: The pagination methods must use a stable argument instead of the raw `arg`. Specifically:
   - A variable named `stableArg` must be created via `useStableQueryArgs(...)`
   - `fetchNextPage` must call `trigger(stableArg, 'forward')`
   - `fetchPreviousPage` must call `trigger(stableArg, 'backward')`

### Expected Behavior

The functions returned by `useInfiniteQuerySubscription` should:
- Maintain referential equality across re-renders when the underlying query state hasn't meaningfully changed
- Not cause unnecessary re-renders of components that depend on these functions
- Work correctly with `useCallback` and `useMemo` dependency arrays

### Technical Constraints

- The fix must preserve all existing functionality and behavior
- The hook must still correctly detect when query arguments change
- TypeScript types must remain valid
- All existing tests must continue to pass

### Resources

- Modified file: `packages/toolkit/src/query/react/buildHooks.ts`
- RTK Query documentation: https://redux-toolkit.js.org/queries/api/createInfiniteQuery
- Issue reference: https://github.com/reduxjs/redux-toolkit/issues/4935
