# Fix Vite 7/8 Bundler Options Compatibility

## Problem

The `@tanstack/start-plugin-core` package has a compatibility issue when used in pnpm workspaces with different Vite versions. The SSR benchmark builds are failing because the plugin's bundler configuration is not being recognized by the consuming application's Vite instance.

## Symptom

When a project using Vite 7 consumes the start-plugin-core from a workspace where the plugin itself resolves to Vite 8 (or vice versa), the build configuration fails. Vite 7 expects `rollupOptions` while Vite 8 expects `rolldownOptions`.

The current implementation in `packages/start-plugin-core/src/utils.ts` attempts dynamic version detection via:
- Import: `import * as vite from 'vite'`
- Export: `export const isRolldown = 'rolldownVersion' in vite`
- Export: `export const bundlerOptionsKey = isRolldown ? 'rolldownOptions' : 'rollupOptions'`

This detection evaluates the plugin's own Vite import rather than the consumer's Vite version, making it unreliable in workspace scenarios.

## Affected Files

- `packages/start-plugin-core/src/plugin.ts` - Main plugin configuration
- `packages/start-plugin-core/src/utils.ts` - Utility functions including bundler detection

## Expected Behavior

The plugin should work correctly with both Vite 7 and Vite 8, regardless of which version the consuming application uses. To achieve this:

1. In `utils.ts`, remove the version detection logic:
   - Remove `export const isRolldown`
   - Remove `export const bundlerOptionsKey`
   - Remove `import * as vite from 'vite'`

2. In `plugin.ts`, update the build configuration to set both bundler option keys simultaneously:
   - Set `rollupOptions: bundlerOptions` for Vite 7 compatibility
   - Set `rolldownOptions: bundlerOptions` for Vite 8 compatibility
   - The value assigned to both keys should use the variable name `bundlerOptions`

Vite ignores unknown configuration keys, so setting both `rollupOptions` and `rolldownOptions` allows the same configuration to work with both Vite versions.

## Verification

After fixing, ensure:
1. The package compiles without TypeScript errors
2. ESLint passes
3. The repository's unit tests pass
4. The repository's type checks pass
5. The repository's build quality checks pass
