# Task: Add deepEqual Comparator to useStore Hooks

## Problem

The `useStore` hooks in `Scripts.tsx` and `headContentUtils.tsx` are causing unnecessary re-renders because they don't use a proper equality comparator.

## Files to Modify

1. `packages/react-router/src/Scripts.tsx` - The Scripts component
2. `packages/react-router/src/headContentUtils.tsx` - The useTags hook and related utilities

## What Needs to Change

The `@tanstack/react-store` library's `useStore` hook accepts an optional third argument: an equality comparator function. Without this comparator, `useStore` uses referential equality by default, which can cause components to re-render even when the derived data hasn't meaningfully changed.

The `@tanstack/router-core` package exports a `deepEqual` function that should be used as the comparator for these `useStore` calls.

### Scripts.tsx Changes

Add `deepEqual` import from `@tanstack/router-core` and use it as the third argument to all `useStore` calls that read from `router.stores.activeMatchesSnapshot`.

### headContentUtils.tsx Changes

Add `deepEqual` to the existing import from `@tanstack/router-core` and use it as the third argument to all `useStore` calls that read from `router.stores.activeMatchesSnapshot`.

## Acceptance Criteria

1. Both files must import `deepEqual` from `@tanstack/router-core`
2. All `useStore` calls that read from `router.stores.activeMatchesSnapshot` must use `deepEqual` as the comparator
3. The code must build successfully (`pnpm build`)
4. Unit tests must pass (`pnpm nx run @tanstack/react-router:test:unit`)

## Hints

- The `useStore` signature is: `useStore(store, selector, comparator?)`
- The `deepEqual` function is already exported from `@tanstack/router-core`
- Look for all places where `useStore(router.stores.activeMatchesSnapshot, ...)` is called
- You'll need to add the third argument to each of these calls
