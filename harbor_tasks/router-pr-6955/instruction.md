# Vite 8 Compatibility Issue in TanStack Start Plugin

## Problem

The `@tanstack/start-plugin-core` package currently hardcodes references to `rollupOptions` when configuring Vite build environments. This works with Vite 7, but Vite 8 uses a different bundler and a renamed configuration key.

Users upgrading to Vite 8 encounter configuration failures because the plugin tries to access `build.rollupOptions` which does not exist in Vite 8.

## Expected Behavior

The plugin must work with both Vite 7 and Vite 8:
- Vite 7 uses the `rollupOptions` configuration key
- Vite 8 uses the `rolldownOptions` configuration key
- Detection happens automatically at runtime without manual configuration

## Required Changes

### utils.ts

The utility file needs to support dynamic bundler configuration selection:

- **Version detection**: Import vite and detect whether Vite 8 (Rolldown) is in use by checking for a distinguishing property in the vite module
- **Configuration key selection**: Export a constant that resolves to the correct key based on the detected Vite version
- **Options retrieval**: Export a function that reads from the appropriate bundler options in the Vite config

The implementation must handle both `rolldownOptions` (Vite 8) and `rollupOptions` (Vite 7) configurations.

### plugin.ts

The plugin currently accesses bundler configuration using a hardcoded key. It must be updated to use the dynamic configuration key from utils.ts.

### preview-server-plugin/plugin.ts

The preview server plugin needs to access the bundler input configuration. It should use the bundler options retrieval function from utils.ts rather than accessing the configuration directly.

## Files to Investigate

- `packages/start-plugin-core/src/utils.ts` - Utility functions
- `packages/start-plugin-core/src/plugin.ts` - Main plugin configuration
- `packages/start-plugin-core/src/preview-server-plugin/plugin.ts` - Preview server configuration

## Notes

- Vite 8 exposes a property in the vite module that distinguishes it from Vite 7
- The fix must remain backward compatible with Vite 7
- When both configuration keys are present in the config, prefer the Vite 8 key