# Fix useStore Re-renders in Head and Scripts Components

## Problem

The React Router's `Scripts` component and the `useTags` hook in `headContentUtils.tsx` are experiencing unnecessary re-renders due to how `useStore` from `@tanstack/react-store` is being used. 

When `useStore` is called without an equality comparator, it uses reference equality by default. This causes components to re-render even when the actual data hasn't changed semantically - for example, when a new array with the same contents is returned from the selector function.

## Files to Fix

1. `packages/react-router/src/Scripts.tsx` - The `Scripts` component that loads script assets
2. `packages/react-router/src/headContentUtils.tsx` - The `useTags` hook that manages head/meta content

## What You Need to Do

1. Import `deepEqual` from `@tanstack/router-core` in both files
2. Add `deepEqual` as the third argument to all `useStore` calls in these components

The `useStore` hook accepts an optional equality comparator as its third argument. Using `deepEqual` will ensure components only re-render when the actual data content changes, not just when object references differ.

## Expected Behavior

After the fix:
- The `Scripts` component should not re-render when the active matches snapshot produces new arrays with the same content
- The `useTags` hook should not cause unnecessary head content updates when route metadata hasn't meaningfully changed
- All existing tests should continue to pass

## Development Guidelines

- Use workspace protocol for internal dependencies (`workspace:*`)
- Run `pnpm test:eslint`, `pnpm test:types`, and `pnpm test:unit` before completing
- Use `pnpm nx run @tanstack/react-router:test:unit` for targeted testing
- Use `pnpm nx run @tanstack/react-router:build` to verify the build succeeds
