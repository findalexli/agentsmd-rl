# Fix Use-Store Re-renders in Head and Scripts Components

## Problem

The React Router's `Scripts` component (`packages/react-router/src/Scripts.tsx`) and the `useTags` hook in `packages/react-router/src/headContentUtils.tsx` experience unnecessary re-renders.

When `useStore` from `@tanstack/react-store` is called with a selector that returns a new array or object on each call, the component re-renders even when the underlying data hasn't changed. This is because `useStore` uses reference equality by default (same as `===`).

## Scope

- `Scripts.tsx` contains 2 `useStore` calls (selecting `assetScripts` via `getAssetScripts` and `scripts` via `getScripts`)
- `headContentUtils.tsx` contains a `useTags` hook with 5 `useStore` calls

## Requirements

The `@tanstack/router-core` package exports a `deepEqual` utility. After the fix:

1. **Scripts.tsx** must contain the import: `import { deepEqual } from '@tanstack/router-core'`
2. **headContentUtils.tsx** must import `deepEqual` from `@tanstack/router-core` (alongside the existing `escapeHtml` import — either `deepEqual, escapeHtml` or `escapeHtml, deepEqual`)
3. All 7 `useStore` calls across both files must pass `deepEqual` as their third argument, formatted with Prettier-compatible multi-line style (e.g., each argument on its own line with `deepEqual,` as the last argument line)
4. In `Scripts.tsx`, the `useStore` calls must produce the patterns `getAssetScripts,\n    deepEqual,` and `getScripts,\n    deepEqual,`
5. In `headContentUtils.tsx`, the `useTags` function must contain exactly 5 `useStore` calls, each with `deepEqual` as its third argument

## Verification

After fixing, run the following commands to verify correctness:
- `pnpm nx run @tanstack/react-router:test:unit -- --run` — Unit tests should pass
- `pnpm nx run @tanstack/react-router:test:types` — TypeScript check should pass
- `pnpm nx run @tanstack/react-router:build` — Build should succeed
- `pnpm nx run @tanstack/react-router:test:build` — Build validation should pass
- `pnpm prettier --experimental-cli --check 'packages/react-router/src/**/*.tsx'` — Formatting should be valid
- `pnpm test:docs` — Docs links should be valid
