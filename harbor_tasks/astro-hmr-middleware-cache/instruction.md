# Fix HMR for Middleware Changes in Astro Dev Server

## Problem

When running `astro dev`, changes to `src/middleware.ts` are not picked up automatically. The middleware continues to use the old version until the dev server is fully restarted. This breaks the Hot Module Replacement (HMR) workflow for middleware.

## Expected Behavior

Editing middleware during `astro dev` should take effect on the next request without requiring a server restart.

## Background

The dev server caches resolved middleware. When a middleware file is modified, the cache must be invalidated so the next request re-resolves the middleware.

The Vite plugin system can detect file changes and send HMR events to clients.

## Verification

After implementing the fix, the following behaviors must be observable in the codebase:

1. The pipeline class has a method to invalidate the middleware cache (with `void` return type) that resets the cache field
2. The DevApp class has a method to invalidate the middleware cache (with `void` return type) that delegates to the pipeline
3. The AstroServerApp class has a method to invalidate the middleware cache (with `void` return type) that delegates to the pipeline
4. The middleware Vite plugin has a `configureServer` hook that watches for file changes using `server.watcher`
5. When middleware files change, an HMR event is dispatched
6. Both dev entrypoints listen for HMR events and respond by clearing the middleware cache
7. A debug log message is emitted when the cache is cleared

## File Locations

The relevant source files are located in:
- `packages/astro/src/core/base-pipeline.ts`
- `packages/astro/src/core/app/dev/app.ts`
- `packages/astro/src/core/app/entrypoints/virtual/dev.ts`
- `packages/astro/src/core/middleware/vite-plugin.ts`
- `packages/astro/src/vite-plugin-app/app.ts`
- `packages/astro/src/vite-plugin-app/createAstroServerApp.ts`
