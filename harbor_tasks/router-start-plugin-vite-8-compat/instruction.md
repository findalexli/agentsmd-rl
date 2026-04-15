# Fix Vite 7/8 Compatibility for `@tanstack/start-plugin-core`

## Problem

The plugin crashes when loaded in a Vite 8+ project. The error occurs because the plugin accesses `build.rollupOptions`, but Vite 8 replaced this property with `build.rolldownOptions` when it adopted the Rolldown bundler.

## Background

- **Vite 7** uses Rollup and stores bundler config under `build.rollupOptions`
- **Vite 8** uses Rolldown and stores the same config under `build.rolldownOptions`

The plugin currently hardcodes `rollupOptions`, which works only for Vite 7.

## What You Need to Do

The plugin needs runtime detection of which bundler is active and must use the correct property name when reading or writing build configuration.

### 1. Add runtime bundler detection

Vite exposes a marker in its module that identifies when Rolldown is in use. Detect this at runtime to determine which bundler is active.

### 2. Export utilities for version-aware bundler access

Export a computed key that resolves to the correct property name (`rolldownOptions` or `rollupOptions`) based on the detected bundler. Also export a helper that reads the bundler options from a build config using the correct property.

### 3. Update plugin to use dynamic property names

Replace all hardcoded references to `rollupOptions` in build configuration with computed property access based on the detected bundler.

## Expected Results

After your changes:
- `pnpm nx run @tanstack/start-plugin-core:build` completes without errors
- `pnpm nx run @tanstack/start-plugin-core:test:types` passes
- `pnpm nx run @tanstack/start-plugin-core:test:eslint` passes
- The plugin works with both Vite 7 and Vite 8 projects

## Key Files

- `packages/start-plugin-core/src/utils.ts` — add the detection utilities and exports
- `packages/start-plugin-core/src/plugin.ts` — update build config property access
- `packages/start-plugin-core/src/preview-server-plugin/plugin.ts` — update server input reading