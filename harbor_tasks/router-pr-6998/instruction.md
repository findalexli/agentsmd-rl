# Fix HeadContent Stylesheet Remounting in Solid Router

## Problem

Users report a Flash of Unstyled Content (FOUC) when using `history.replaceState()` in applications built with `@tanstack/solid-router`. The issue manifests as:

1. Stylesheet links in `<head>` unmount and remount when `window.history.replaceState()` is called
2. This causes a brief "flash" where styles are lost and reapplied
3. The same issue occurs during repeated navigation between routes

When state changes trigger re-renders, the stylesheet link elements are being recreated rather than preserved, causing the visual artifacts.

## Expected Behavior

Stylesheet links provided via the manifest should remain as the same DOM elements throughout history state changes and navigations, as long as their content hasn't meaningfully changed.

## Test Requirements

The fix must satisfy the following code pattern requirements (verified by automated tests):

1. The `useTags` function in `packages/solid-router/src/headContentUtils.tsx` must import `replaceEqualDeep` from `@tanstack/router-core`

2. The `useTags` function must return `Solid.createMemo` with a callback that receives a `prev` parameter

3. The `useTags` function must call `replaceEqualDeep(prev, next)` to compare the previous and next tag arrays

## Verification

After applying the fix:
- All Solid Router unit tests must pass (`pnpm nx run @tanstack/solid-router:test:unit`)
- TypeScript type checking must pass (`pnpm nx run @tanstack/solid-router:test:types`)
- The build must succeed (`pnpm nx run @tanstack/solid-router:build`)
- ESLint checks must pass (`pnpm nx run @tanstack/solid-router:test:eslint`)
- Package exports must be valid (`pnpm nx run @tanstack/solid-router:test:build`)
