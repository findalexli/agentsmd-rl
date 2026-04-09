# Fix Retained Promise References in Router Core

There is a memory management issue in the TanStack Router core where promise references are retained longer than necessary during route loading and location commits.

## Problem

During navigation cycles, certain promise references are captured but never released, potentially causing memory accumulation:

1. In `packages/router-core/src/load-matches.ts`, the `executeBeforeLoad` function captures the previous `loadPromise` but the reference persists after resolution
2. In `packages/router-core/src/load-matches.ts`, the `loadRouteMatch` function resolves promises but doesn't clear the references
3. In `packages/router-core/src/router.ts`, the `commitLocation` method has similar promise retention in `previousCommitPromise`

## Files to Modify

- `packages/router-core/src/load-matches.ts` - Fix `prevLoadPromise` and `loadPromise` retention
- `packages/router-core/src/router.ts` - Fix `previousCommitPromise` retention

## What to Look For

Search for patterns where promise references are captured with `const` but should allow reassignment to `undefined` after resolution. The fix involves:

1. Changing variable declarations from `const` to `let` for promise references that need to be cleared
2. Setting these references to `undefined` after the promise resolves

## Testing

After making changes:
1. Build the package: `pnpm nx run @tanstack/router-core:build`
2. Run type checks: `pnpm nx run @tanstack/router-core:test:types`
3. Run unit tests: `pnpm nx run @tanstack/router-core:test:unit`

## References

- The router core uses `createControlledPromise` for promise management
- Look for patterns involving `loadPromise`, `loaderPromise`, and `commitLocationPromise`
- The `match._nonReactive` object holds non-reactive promise references
