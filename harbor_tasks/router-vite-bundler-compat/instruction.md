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
- Detect whether Rolldown is in use by checking the vite module

### Configuration Keys
- The implementation must handle both `rolldownOptions` (Vite 8) and `rollupOptions` (Vite 7) keys
- When reading configuration, check for `rolldownOptions` first, then fall back to `rollupOptions`

### Utility Functions
Create utility functions in a shared utilities module to centralize the bundler compatibility logic:
- A function that detects if Rolldown is the active bundler
- A function that returns the correct configuration key name based on the detected bundler
- A function that reads bundler options from a build config using the appropriate key

### Integration Requirements
- Use computed property access for dynamic key selection instead of hardcoded `rollupOptions:` in build configuration objects
- Remove all hardcoded `rollupOptions:` references in build config sections
- Update the preview server plugin to use the utility function for reading server input

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
