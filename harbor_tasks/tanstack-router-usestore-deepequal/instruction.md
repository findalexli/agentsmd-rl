# Fix Use-Store Re-renders in Head and Scripts Components

## Problem

The React Router's `Scripts` component (`packages/react-router/src/Scripts.tsx`) and the `useTags` hook in `packages/react-router/src/headContentUtils.tsx` experience unnecessary re-renders.

When `useStore` from `@tanstack/react-store` is called with a selector that returns a new array or object on each call, the component re-renders even when the underlying data hasn't changed. This is because `useStore` uses reference equality by default (same as `===`).

## Specific Files

- `packages/react-router/src/Scripts.tsx` — The `Scripts` component that renders script tags
- `packages/react-router/src/headContentUtils.tsx` — Contains the `useTags` hook that manages head/meta content

Both files call `useStore` with selectors that return newly-constructed arrays on every invocation, even when the matched route data is semantically identical.

## Hint

The `@tanstack/react-store` package's `useStore` hook accepts an optional third argument: a comparison function. Using a deep-equality comparator in this argument prevents unnecessary re-renders when the selector produces a new object reference but the actual content is the same.

The `@tanstack/router-core` package exports comparison utilities that may be useful.

## Verification

After fixing, run the following commands to verify correctness:
- `pnpm nx run @tanstack/react-router:test:unit -- --run` — Unit tests should pass
- `pnpm nx run @tanstack/react-router:test:types` — TypeScript check should pass
- `pnpm nx run @tanstack/react-router:build` — Build should succeed
- `pnpm nx run @tanstack/react-router:test:build` — Build validation should pass
- `pnpm prettier --experimental-cli --check 'packages/react-router/src/**/*.tsx'` — Formatting should be valid
- `pnpm test:docs` — Docs links should be valid