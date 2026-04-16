# Fix Unnecessary Re-renders in Head and Scripts Components

## Problem

The React Router's `Scripts` component in `packages/react-router/src/Scripts.tsx` and the `useTags` hook in `packages/react-router/src/headContentUtils.tsx` experience unnecessary re-renders.

The `useStore` hook (from `@tanstack/react-store`) is called with selectors that return new array or object references on every invocation. Because `useStore` defaults to reference equality (`===`), components re-render even when the underlying data hasn't meaningfully changed.

## Affected Code

- **`packages/react-router/src/Scripts.tsx`** — contains 2 `useStore` calls that lack a comparator
- **`packages/react-router/src/headContentUtils.tsx`** — the `useTags` hook contains 5 `useStore` calls that lack a comparator

All 7 `useStore` calls across both files are affected and need to be fixed.

## What Needs to Happen

The `useStore` hook accepts an optional third argument: a comparator function used to determine whether the selected state has actually changed. Currently, none of the 7 `useStore` calls in these two files provide a comparator, so they fall back to reference equality.

Each of these `useStore` calls should be updated to include a suitable equality comparator as its third argument so that re-renders only occur when the selected data has meaningfully changed. Look at what utilities the `@tanstack/router-core` package already exports that could serve as a comparator.

## Verification

After fixing, ensure the following all pass:
- `pnpm nx run @tanstack/react-router:test:unit -- --run` — Unit tests
- `pnpm nx run @tanstack/react-router:test:types` — TypeScript type checking
- `pnpm nx run @tanstack/react-router:build` — Build
- `pnpm nx run @tanstack/react-router:test:build` — Build validation
- `pnpm prettier --experimental-cli --check 'packages/react-router/src/**/*.tsx'` — Formatting
- `pnpm test:docs` — Documentation links
