# Fix Vite 7/8 Compatibility for `@tanstack/start-plugin-core`

## Problem

The plugin crashes when loaded in a Vite 8+ project with an error related to accessing bundler configuration. This happens because Vite 8 replaced `build.rollupOptions` with `build.rolldownOptions` when it adopted the Rolldown bundler, but the plugin uses hardcoded references to `rollupOptions`.

## Symptom

When the plugin runs in a Vite 8 environment, configuration access fails because:
- **Vite 7** uses Rollup and stores bundler config under `build.rollupOptions`
- **Vite 8** uses Rolldown and stores the same config under `build.rolldownOptions`

The plugin needs to detect which bundler is active at runtime and use the correct property name.

## Required Changes

You must implement and use these specific utilities (exact names required):

### 1. In `packages/start-plugin-core/src/utils.ts`

Export these utilities:
- `isRolldown` - a boolean detecting if Rolldown is active by checking if `'rolldownVersion'` exists in the vite module (use `import * as vite from 'vite'` for the import)
- `bundlerOptionsKey` - a computed key that resolves to `'rolldownOptions'` when `isRolldown` is true, otherwise `'rollupOptions'`
- `getBundlerOptions(build)` - a helper function that reads bundler options from a build config, checking `build?.rolldownOptions` first, then falling back to `build?.rollupOptions`

### 2. In `packages/start-plugin-core/src/plugin.ts`

Update the plugin to:
- Import `bundlerOptionsKey` and `getBundlerOptions` from `'./utils'` (exact import: `import { bundlerOptionsKey, getBundlerOptions } from './utils'`)
- Replace hardcoded `rollupOptions` property access with computed `[bundlerOptionsKey]` for both client and server build configurations
- Use `getBundlerOptions()` when reading server bundler options

### 3. In `packages/start-plugin-core/src/preview-server-plugin/plugin.ts`

Update the preview server plugin to:
- Import `getBundlerOptions` from `'../utils'` (exact import: `import { getBundlerOptions } from '../utils'`)
- Use `getBundlerOptions(serverEnv?.build)?.input` to read the server input instead of direct property access

## Expected Results

After your changes:
- `pnpm nx run @tanstack/start-plugin-core:build` completes without errors
- `pnpm nx run @tanstack/start-plugin-core:test:types` passes
- `pnpm nx run @tanstack/start-plugin-core:test:eslint` passes
- The plugin works with both Vite 7 and Vite 8 projects
