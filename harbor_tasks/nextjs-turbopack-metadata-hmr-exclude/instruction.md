# Turbopack: metadata routes not hot-reloading in dev mode

## Problem

Metadata routes (`manifest.ts`, `robots.ts`, `sitemap.ts`, `icon.tsx`, `apple-icon.tsx`, etc.) are not being hot-reloaded when running `next dev` with Turbopack. When you edit a metadata route file (e.g., change the `name` field in `manifest.ts`), the changes are not reflected on subsequent requests to the corresponding endpoint (e.g., `/manifest.webmanifest`). The stale content persists until you do a full server restart.

This regression was introduced when server HMR was extended from app pages to all `app`-type entries, including route handlers. The in-place module update model used by server HMR is not appropriate for metadata routes, which serve HTTP responses directly and need their caches fully invalidated to pick up file changes.

## Expected Behavior

When a metadata route file is modified during development, the next request to that endpoint should return the updated content without requiring a server restart. Regular route handlers and app pages should continue to use server HMR as before.

## Files to Look At

- `packages/next/src/server/dev/hot-reloader-turbopack.ts` — the Turbopack hot reloader, specifically the `clearRequireCache()` logic and the `usesServerHmr` condition that decides whether to skip cache invalidation
- `packages/next/src/lib/metadata/is-metadata-route.ts` — utility functions for identifying metadata routes
