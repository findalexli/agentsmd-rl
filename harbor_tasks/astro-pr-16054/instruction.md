# Middleware HMR Bug

## What's broken

When running `astro dev`, changes to middleware files (e.g., `src/middleware.ts`) are not picked up by the development server. Users must restart the entire dev server for middleware changes to take effect.

## Expected behavior

Editing a middleware file during `astro dev` should cause the middleware to reload on the next request, without requiring a full server restart.

## Technical approach

The fix requires three things:

1. **Cache invalidation**: Add a method that clears the resolved middleware cache. When called, the middleware will be re-resolved on the next request.

2. **File watching**: Register a file watcher in the dev server to detect when middleware files under `srcDir` are modified.

3. **HMR signaling**: When a middleware file changes, send a hot module replacement (HMR) event to notify the running server, which should then clear the middleware cache.

The project linter (Biome) must pass on all modified files.