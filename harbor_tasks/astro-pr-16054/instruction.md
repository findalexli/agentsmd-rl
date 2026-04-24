# Middleware HMR Bug

## What's broken

When running `astro dev`, changes to middleware files (e.g., `src/middleware.ts`) are not picked up by the development server. Users must restart the entire dev server for middleware changes to take effect.

## Expected behavior

Editing a middleware file during `astro dev` should cause the middleware to reload on the next request, without requiring a full server restart.

## Technical approach

The fix requires three things:

1. **Cache invalidation**: Add a method that clears the resolved middleware cache. When called, the middleware will be re-resolved on the next request. The method should reset `resolvedMiddleware` to `undefined`.

2. **File watching**: Register a file watcher in the dev server to detect when middleware files under `srcDir` are modified. The watcher should check if the changed file is under `srcDir` and is a middleware file (starts with `middleware.`).

3. **HMR signaling**: When a middleware file changes, send a hot module replacement (HMR) event to notify the running server, which should then clear the middleware cache. The server-side listeners should call the cache invalidation method when they receive this event.

The key classes involved are:
- `Pipeline` (in `packages/astro/src/core/base-pipeline.ts`) - holds the `resolvedMiddleware` cache
- `AstroServerApp` (in `packages/astro/src/vite-plugin-app/app.ts`) - the main dev server app
- `DevApp` (in `packages/astro/src/core/app/dev/app.ts`) - development app wrapper
- The middleware Vite plugin (in `packages/astro/src/core/middleware/vite-plugin.ts`)
- The virtual dev module (in `packages/astro/src/core/app/entrypoints/virtual/dev.ts`)
- `createAstroServerApp` (in `packages/astro/src/vite-plugin-app/createAstroServerApp.ts`)

The project linter (Biome) must pass on all modified files.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
