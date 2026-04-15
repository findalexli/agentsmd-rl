# Fix Retained Promise References in Router Core

There is a memory management issue in the TanStack Router core where promise references are retained longer than necessary during route loading and location commits.

## Problem

During navigation cycles, certain promise references are captured but never released, potentially causing memory accumulation:

1. In `packages/router-core/src/load-matches.ts`, the `executeBeforeLoad` function captures `match._nonReactive.loadPromise` but this reference persists after the promise resolves
2. In `packages/router-core/src/load-matches.ts`, the `loadRouteMatch` function resolves `match._nonReactive.loadPromise` but the reference remains set
3. In `packages/router-core/src/router.ts`, the `commitLocation` method captures `this.commitLocationPromise` but doesn't release it after resolution

## Files to Modify

- `packages/router-core/src/load-matches.ts` - Look for `executeBeforeLoad` and `loadRouteMatch` functions
- `packages/router-core/src/router.ts` - Look for `commitLocation` method

## Testing

After making changes:
1. Build the package: `pnpm nx run @tanstack/router-core:build`
2. Run type checks: `pnpm nx run @tanstack/router-core:test:types`
3. Run unit tests: `pnpm nx run @tanstack/router-core:test:unit`

## References

- The router core uses `createControlledPromise` for promise management
- The `match._nonReactive` object holds non-reactive promise references
