# Fix Vite 7/8 Compatibility for Bundler Options

## Problem

The `start-plugin-core` package has a bug where it tries to detect the Vite version at the plugin's import time. This detection fails in pnpm workspaces because:

- The plugin might resolve one version of Vite for its own dependencies
- But the consumer project might be using a different Vite version
- This causes the plugin to set the wrong bundler options key for the consumer's Vite version
- The result is build failures with "Could not resolve entry module" errors

## What You Need To Do

Fix the bundler options handling in the `start-plugin-core` package so that it works correctly with both Vite 7 and Vite 8, regardless of which version the plugin itself resolves.

### Specific Requirements

1. **In `packages/start-plugin-core/src/utils.ts`:**
   - Remove the `bundlerOptionsKey` export
   - Remove the `isRolldown` export
   - Keep the `getBundlerOptions` function
   - Remove any Vite version detection logic (checking for `rolldownVersion` in vite)

2. **In `packages/start-plugin-core/src/plugin.ts`:**
   - Remove any import or reference to `bundlerOptionsKey`
   - Import `getBundlerOptions` from `./utils`
   - For the client environment build configuration, create a variable named exactly `bundlerOptions` containing the build input configuration, then set both `rollupOptions: bundlerOptions` and `rolldownOptions: bundlerOptions` using the same object reference
   - For the server environment build configuration, do the same: create a `bundlerOptions` variable and use it for both `rollupOptions` and `rolldownOptions`
   - This ensures Vite 7 reads `rollupOptions` and Vite 8 reads `rolldownOptions`, with both pointing to the same configuration object

## Expected Behavior

After the fix:
- Builds should succeed whether the consumer uses Vite 7 or Vite 8
- The code must use a variable named `bundlerOptions` to hold the shared configuration
- Both `rollupOptions: bundlerOptions` and `rolldownOptions: bundlerOptions` must be present for both client and server environments
- Using the same object reference for both options avoids Vite 8 deprecation warnings
- TypeScript compilation, ESLint, and unit tests must continue to pass

## Testing Your Fix

After making changes:
1. TypeScript should compile (`pnpm nx run @tanstack/start-plugin-core:test:types`)
2. Package should build (`pnpm nx run @tanstack/start-plugin-core:build`)
3. ESLint should pass (`pnpm nx run @tanstack/start-plugin-core:test:eslint`)
4. Any existing unit tests should still pass
