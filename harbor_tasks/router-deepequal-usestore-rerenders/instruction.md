# Fix: Reduce unnecessary re-renders in Scripts and Head components

## Problem

The `Scripts` and `Head` components in the react-router package are experiencing unnecessary re-renders. Components that subscribe to the router's store are re-rendering even when the data they depend on hasn't meaningfully changed.

## Affected Files

- `packages/react-router/src/Scripts.tsx`
- `packages/react-router/src/headContentUtils.tsx`

## Symptom

When the router's internal store updates, these components re-render even if the actual data they use (scripts, links, styles, etc.) is unchanged. This causes performance issues in applications using these components.

## Investigation Steps

1. Examine how the `Scripts` and `Head` components subscribe to the router store
2. Identify the store subscription mechanism used (`useStore` from `@tanstack/react-store`)
3. Determine why components re-render when store references change even if values are equal
4. Find an existing equality function in `@tanstack/router-core` that can compare objects deeply

## Verification

After making changes:
1. Run type checks: `pnpm nx run @tanstack/react-router:test:types`
2. Run unit tests: `pnpm nx run @tanstack/react-router:test:unit`
3. Run lint: `pnpm nx run @tanstack/react-router:test:eslint`

## Notes

- Environment variables `CI=1 NX_DAEMON=false` may be needed when running Nx commands
- The `@tanstack/router-core` package exports utility functions used across the router packages
