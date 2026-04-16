# Vue Router Link Refactoring

## Problem

The vue-router `Link` component behaves inconsistently compared to the React and Solid implementations. While React and Solid pass options directly to `buildLocation` and let it handle the `from` default internally, the vue-router implementation manually computes `from` using store data before passing options. This creates unnecessary coupling between the Link component and internal router stores that the other implementations don't have.

The manual computation relies on two specific stores:
- `lastMatchId` in `packages/router-core/src/stores.ts` - stores the ID of the last match
- `lastMatchRouteFullPath` in `packages/vue-router/src/routerStores.ts` - stores the full path of the last match route

In `packages/router-core/src/router.ts`, the code currently accesses `this.stores.lastMatchId.state` to get the last match ID. This should instead derive the last match ID directly from `this.stores.matchesId.state`.

In `packages/vue-router/src/link.tsx`, the code currently has:
- A computed wrapper: `const _options = Vue.computed(() => ({ ...options, from: from.value }))`
- References to `router.stores.lastMatchRouteFullPath` for determining the `from` value
- SSR section (where `isServer ?? router.isServer` is checked) that calls `router.buildLocation` with wrapped options including a `from` field
- Client section that spreads `..._options.value` instead of `...options`

## Goal

Refactor the vue-router `Link` component so it delegates `from` handling to `buildLocation`, matching the React and Solid patterns. This should eliminate the need for the `lastMatchId` and `lastMatchRouteFullPath` stores that only exist to support this manual computation.

## Expected Outcomes

After the refactoring:
- `packages/router-core/src/stores.ts` should not contain `lastMatchId` in the interface or store creation
- `packages/router-core/src/stores.ts` should only import `arraysEqual` from `'./utils'` (the `last` import should be removed)
- `packages/router-core/src/router.ts` should contain the string `last(this.stores.matchesId.state)` and should NOT contain `this.stores.lastMatchId.state`
- `packages/vue-router/src/routerStores.ts` should not contain `lastMatchRouteFullPath`
- `packages/vue-router/src/link.tsx` should NOT contain `router.stores.lastMatchRouteFullPath`
- `packages/vue-router/src/link.tsx` should NOT contain `const _options = Vue.computed`
- `packages/vue-router/src/link.tsx` should NOT contain `..._options.value`
- The SSR section in `packages/vue-router/src/link.tsx` should contain `router.buildLocation(options as any)` (passed directly without a `from` field)

The refactoring should preserve all existing functionality - builds, type checks, unit tests, and lint checks must continue to pass.
