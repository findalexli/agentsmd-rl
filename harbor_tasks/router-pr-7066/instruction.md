# TanStack Router: Fix scroll position reset after SSR hydration

## The Problem

In non-SPA SSR mode, after the page hydrates, the user's scroll position unexpectedly resets to the hash anchor when:
- Hovering over a link triggers route preloading
- Calling `router.invalidate()`

The URL hasn't changed, but the router re-scrolls to the hash anchor anyway.

## Expected Behavior

After SSR hydration completes in non-SPA mode:
1. Hovering over links with route preloading should NOT cause scroll jumps
2. Calling `router.invalidate()` should NOT reset scroll position to the hash
3. The scroll position should remain stable until an actual navigation occurs

## Implementation Requirements

When you implement the fix, the following must be true:

1. The file `packages/router-core/src/ssr/ssr-client.ts` must contain the string `resolvedLocation.setState` within the non-SPA SSR hydration block (the code path where `!hasSsrFalseMatches && !isSpaMode` is true)

2. Within that same non-SPA SSR block, there must be a comment explaining the fix that contains at least one of these phrases: `later load cycles`, `preloads`, or `invalidations`

3. The SPA mode hydration path must remain intact and continue to include:
   - The string `if (isSpaMode)`
   - The string `loadPromise.then`
   - The string `resolvedLocation.setState`

4. The non-SPA SSR block must NOT call `router.load()` in executable code (it may appear in comments)

5. The file `packages/router-core/src/ssr/ssr-client.ts` must use spaces for indentation (no tab characters)

## Verification

After implementing your fix:
- TypeScript compilation must pass: `pnpm --filter @tanstack/router-core run test:types`
- Build must succeed: `pnpm --filter @tanstack/router-core run build`
- Unit tests must pass: `pnpm --filter @tanstack/router-core run test:unit -- --run`
- ESLint must pass: `pnpm nx run @tanstack/router-core:test:eslint --skipRemoteCache`
- Build check must pass: `pnpm nx run @tanstack/router-core:test:build --skipRemoteCache`
