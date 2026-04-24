# Fix Vite 7/8 Compatibility for `@tanstack/start-plugin-core`

## Problem

The plugin crashes when loaded in a Vite 8+ project with an error related to accessing bundler configuration. Vite 8 changed how it stores bundler options compared to Vite 7, but the plugin uses hardcoded property names that don't exist in Vite 8.

## Symptom

When the plugin runs in a Vite 8 environment, configuration access fails because the property name used by the plugin doesn't exist on the build config object. The plugin needs to detect which Vite version is running and use the correct property name at runtime.

## Required Changes

### 1. In `packages/start-plugin-core/src/utils.ts`

Add runtime detection of the active bundler and export helper utilities:
- Detect whether the project is using Vite 7 or Vite 8
- Export a function that returns the correct bundler options key for the current environment

### 2. In `packages/start-plugin-core/src/plugin.ts`

Update the plugin to use dynamic property access for build configuration:
- Import the bundler utilities from utils
- Replace hardcoded property access with dynamic lookup for both client and server build configurations

### 3. In `packages/start-plugin-core/src/preview-server-plugin/plugin.ts`

Update the preview server plugin to use the bundler helper:
- Import the bundler utilities from utils
- Use the helper function to read the server input from bundler options instead of direct property access

## Expected Results

After your changes:
- `pnpm nx run @tanstack/start-plugin-core:build` completes without errors
- `pnpm nx run @tanstack/start-plugin-core:test:types` passes
- `pnpm nx run @tanstack/start-plugin-core:test:eslint` passes
- The plugin works with both Vite 7 and Vite 8 projects