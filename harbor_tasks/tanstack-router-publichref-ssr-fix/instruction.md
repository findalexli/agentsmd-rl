# Fix publicHref Calculation Mismatch in SSR

## Problem

There's a mismatch between how `parseLocation` and `buildLocation` calculate the `publicHref` in the router core. This causes loaders to run twice during SSR hydration when URLs contain encoded characters.

## Symptom

When the router hydrates on the client after SSR:
1. The server runs loaders and renders the page
2. On hydration, the client-side router runs loaders **again** because it thinks the location has changed
3. This happens because `buildLocation` returns a different `publicHref` than what `parseLocation` computed

The specific issue is that `buildLocation` was using the raw `href` (which may have encoded characters) for `publicHref`, while `parseLocation` uses `pathname + searchStr + hash` (processed/consistent format).

## Files to Modify

- `packages/router-core/src/router.ts` - Find the `buildLocation` method's return statement

## Hints

1. Look for the `buildLocation` function in `packages/router-core/src/router.ts`
2. Find where `publicHref` is set in the return object
3. The fix should align `publicHref` with how `parseLocation` calculates it
4. Both should use the same calculation: `pathname + searchStr + hash`

## Testing

After your fix:
1. Build the package: `pnpm nx run @tanstack/router-core:build`
2. Run router-core tests: `pnpm nx run @tanstack/router-core:test:unit`

The build should succeed and tests should pass. The key behavioral change is that `publicHref` now consistently uses the processed path components rather than the raw href input.
