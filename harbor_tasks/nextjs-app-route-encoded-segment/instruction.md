# Bug: URL-encoded dynamic placeholders treated as static segments

## Problem

When an app route pathname contains URL-encoded square brackets — for example `%5BprojectSlug%5D` instead of `[projectSlug]` — the route parser in `packages/next/src/shared/lib/router/routes/app.ts` treats them as static segments rather than dynamic ones.

This causes fallback parameters to be missing for those segments, which leads to incorrect rendering when users navigate to pages with URL-encoded dynamic placeholders (e.g., via segment-prefetch responses).

## Reproduction

Consider a route tree like `/[teamSlug]/[projectSlug]`. If a page is reached via `/vercel/%5BprojectSlug%5D`, the route parser should recognize `%5BprojectSlug%5D` as the dynamic segment `[projectSlug]`. Instead, it treats it as a literal static segment, so `projectSlug` is never included in fallback params.

## Expected behavior

The route parser should decode URL-encoded segments before checking whether they match dynamic segment patterns. If decoding reveals a valid dynamic segment (e.g., `[param]`, `[...param]`, `[[...param]]`), it should be treated as dynamic.

## Files to investigate

- `packages/next/src/shared/lib/router/routes/app.ts` — the `parseAppRoute` function iterates over pathname segments and calls `parseAppRouteSegment`, but does not account for URL encoding.
