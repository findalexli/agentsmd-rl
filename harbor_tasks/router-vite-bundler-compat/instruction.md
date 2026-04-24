# Task: Add Vite 7/8 Bundler Compatibility

## Problem

The plugin currently hardcodes references to `rollupOptions` in several places. This breaks compatibility with Vite 8+, which uses Rolldown instead of Rollup. In Vite 8, the configuration key `build.rollupOptions` has been renamed to `build.rolldownOptions`.

## Symptoms

- The plugin only works with Vite 7.x (Rollup-based)
- With Vite 8.x (Rolldown-based), the plugin fails to correctly read or write bundler configuration
- Server input resolution and client build configuration use hardcoded `rollupOptions` key
- Accessing `build.rollupOptions` on a Vite 8 project returns `undefined`, causing the plugin to malfunction

## Required Implementation

The plugin must work with both Vite 7.x and Vite 8.x. Implement runtime bundler detection and configuration key selection:

### Detection Logic
- Detect whether Rolldown is in use by checking the vite module for a Rolldown-specific property

### Configuration Keys
- The implementation must handle both `rolldownOptions` (Vite 8) and `rollupOptions` (Vite 7) keys
- When reading configuration, check for `rolldownOptions` first, then fall back to `rollupOptions`

### Utility Module
Create a shared utilities module at `packages/start-plugin-core/src/utils.ts` that centralizes the bundler compatibility logic:
- Bundler detection: determine at runtime whether the active bundler is Rolldown or Rollup (detect by checking for `rolldownVersion` property in the vite module)
- Key selection: provide the correct configuration key based on detected bundler — either `rolldownOptions` (Vite 8) or `rollupOptions` (Vite 7)
- Options reading: export a function that reads bundler options from a build config using the appropriate key

### File Paths and Integration Points
- The main plugin at `packages/start-plugin-core/src/plugin.ts` must import from `./utils`
- The preview server plugin at `packages/start-plugin-core/src/preview-server-plugin/plugin.ts` must import from `../utils`
- Both plugins must use the utility module's option reader (not direct property access) to read `build.rolldownOptions.input` or `build.rollupOptions.input`

## Validation

Run the following from the package directory to validate your changes:
- `pnpm test:types` - TypeScript type checking
- `pnpm test:eslint` - Linting
- `pnpm build` - Build the package
- `pnpm test:unit` - Run unit tests (if available)

## Notes

- Detection should happen at runtime by inspecting the vite module
- Maintain backward compatibility with Vite 7
- Keep detection logic centralized in a common utilities location