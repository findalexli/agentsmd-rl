# Preserve HTTP Access Fallbacks During Prerender Recovery

## Problem

When a `notFound()`, `forbidden()`, or `unauthorized()` call is made inside a page that uses `cacheComponents` mode (with Suspense in the layout), the client receives a "Connection closed" error instead of the custom error boundary.

The prerender recovery path falls back to a generic error shell flow for all errors. In the `cacheComponents` case, this produces:
- Error HTML rendered from the generic `ErrorApp`
- Flight data reused from the aborted prerender prelude
- References to Flight chunks that were never emitted

This means custom `not-found.tsx`, `forbidden.tsx`, and `unauthorized.tsx` boundaries are not rendered when these errors escape into the outer prerender recovery path during cache component rendering.

## Expected Behavior

When an HTTP access fallback error (404/403/401) occurs during prerender and a matching boundary exists in the route tree:
- The system should find the deepest matching HTTP fallback boundary in the loader tree
- It should rerender the normal app router payload with that segment-scoped fallback instead of the generic error shell
- The Flight stream should be properly handled so both the HTML renderer and the prerender buffer can consume it
- If no matching boundary exists, the existing generic error handling should still be used

## Files to Look At

- `packages/next/src/server/app-render/app-render.tsx` — The main app rendering pipeline, including the prerender recovery path that handles errors during static generation
- `packages/next/src/server/app-render/create-component-tree.tsx` — Creates the React component tree from the loader tree; needs to support rendering scoped fallbacks at matched boundaries
