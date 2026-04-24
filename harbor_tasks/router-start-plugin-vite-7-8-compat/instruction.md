# Fix Vite 7/8 Compatibility for Bundler Options

## Problem

The `start-plugin-core` package has a bug that causes builds to fail when used in pnpm workspaces with certain Vite version configurations. The issue stems from how the plugin determines which bundler options key to use at import time. When the resolved Vite version differs between the plugin's dependencies and the consumer's project, the wrong bundler options key gets set, resulting in "Could not resolve entry module" build failures.

## What You Need To Do

Fix the bundler options handling in the `start-plugin-core` package so that builds succeed correctly regardless of which Vite version the consumer project uses.

### Specific Requirements

1. **In `packages/start-plugin-core/src/utils.ts`:**
   - Remove the `bundlerOptionsKey` export
   - Remove the `isRolldown` export
   - Keep the `getBundlerOptions` function
   - Remove any Vite version detection logic that checks for version-specific properties

2. **In `packages/start-plugin-core/src/plugin.ts`:**
   - Remove any import or reference to `bundlerOptionsKey`
   - Import `getBundlerOptions` from `./utils`
   - For the client environment build configuration, set both `rollupOptions` and `rolldownOptions` to the same configuration object
   - For the server environment build configuration, do the same: set both `rollupOptions` and `rolldownOptions` to the same configuration object

## Expected Behavior

After the fix:
- Builds should succeed whether the consumer uses Vite 7 or Vite 8
- Both `rollupOptions` and `rolldownOptions` must be set for both client and server environments
- Using the same object reference for both options avoids Vite 8 deprecation warnings
- TypeScript compilation, ESLint, and unit tests must continue to pass

## Testing Your Fix

After making changes:
1. TypeScript should compile (`pnpm nx run @tanstack/start-plugin-core:test:types`)
2. Package should build (`pnpm nx run @tanstack/start-plugin-core:build`)
3. ESLint should pass (`pnpm nx run @tanstack/start-plugin-core:test:eslint`)
4. Any existing unit tests should still pass
