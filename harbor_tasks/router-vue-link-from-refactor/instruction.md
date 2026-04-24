# Vue Router Link Refactoring

## Problem

The vue-router `Link` component behaves inconsistently compared to the React and Solid implementations. While React and Solid pass options directly to `buildLocation` and let it handle the `from` default internally, the vue-router implementation manually computes `from` using store data before passing options. This creates unnecessary coupling between the Link component and internal router stores that the other implementations don't have.

Two internal stores exist solely to support this manual computation: one for the last match ID and one for the last match's full path. The router.ts file currently accesses one of these stores by name to derive the last match ID.

## Goal

Refactor the vue-router `Link` component so it delegates `from` handling to `buildLocation`, matching the React and Solid patterns. This should eliminate the need for the two stores that only exist to support manual `from` computation.

## Expected Outcomes

After the refactoring, the following should be true:

- The `stores.ts` file should no longer expose a `lastMatchId` store in its interface or create one in its implementation
- The `stores.ts` file should only import `arraysEqual` from utils (no `last` import needed)
- The `router.ts` file should derive the last match ID by applying `last()` to the matches array in state, not by accessing a dedicated store
- The `routerStores.ts` file should no longer contain a `lastMatchRouteFullPath` store
- The `link.tsx` file should not reference `lastMatchRouteFullPath` store directly
- The `link.tsx` file should not use a computed wrapper around the options to inject `from`
- The SSR section in `link.tsx` should pass options directly to `buildLocation` without pre-wrapping them
- In client-side code, `link.tsx` should spread `options` directly rather than `_options.value`

All builds, type checks, unit tests, and lint checks must continue to pass after the refactoring.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
