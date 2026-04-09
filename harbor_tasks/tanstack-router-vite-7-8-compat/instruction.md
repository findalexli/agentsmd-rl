# Fix Vite 7/8 Compatibility in start-plugin-core

The `@tanstack/start-plugin-core` package needs to support both Vite 7 and Vite 8. In Vite 8, the bundler changed from Rollup to Rolldown, and the configuration option `build.rollupOptions` was renamed to `build.rolldownOptions`.

## Problem

Currently, the plugin hardcodes `rollupOptions` in several places:
- `packages/start-plugin-core/src/plugin.ts` - in the client and server environment configurations
- `packages/start-plugin-core/src/preview-server-plugin/plugin.ts` - when reading the server input

This causes the plugin to fail with Vite 8 because it tries to write to `rollupOptions` instead of `rolldownOptions`.

## What You Need to Do

1. **Add runtime detection** in `packages/start-plugin-core/src/utils.ts`:
   - Detect whether Rolldown is available by checking if `'rolldownVersion'` exists in the `vite` module
   - Export a constant `isRolldown` that indicates which bundler is in use
   - Export a constant `bundlerOptionsKey` that returns `'rolldownOptions'` when using Rolldown, or `'rollupOptions'` otherwise
   - Export a function `getBundlerOptions(build)` that reads from either `build.rolldownOptions` or `build.rollupOptions`

2. **Update `packages/start-plugin-core/src/plugin.ts`**:
   - Import `bundlerOptionsKey` and `getBundlerOptions` from utils
   - Replace hardcoded `rollupOptions` with the dynamic `bundlerOptionsKey` in environment configs
   - Use `getBundlerOptions()` when reading existing bundler configuration

3. **Update `packages/start-plugin-core/src/preview-server-plugin/plugin.ts`**:
   - Import `getBundlerOptions` from utils
   - Use `getBundlerOptions()` when reading the server input

## Files to Modify

- `packages/start-plugin-core/src/utils.ts` - add the detection logic
- `packages/start-plugin-core/src/plugin.ts` - use the new utilities
- `packages/start-plugin-core/src/preview-server-plugin/plugin.ts` - use the new utilities

After making changes, run `pnpm nx run @tanstack/start-plugin-core:build` to verify the package compiles without errors.
