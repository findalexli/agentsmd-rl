# Fix Vite 8 Compatibility: Support both `rollupOptions` and `rolldownOptions`

## Problem

The `@tanstack/start-plugin-core` package currently hardcodes references to `build.rollupOptions` in its Vite plugin configuration. Vite 8+ uses Rolldown instead of Rollup and has renamed this property to `build.rolldownOptions`. This causes the plugin to fail with Vite 8.

The affected files are:
- `packages/start-plugin-core/src/plugin.ts` - Uses `rollupOptions` for client and server environment build configs
- `packages/start-plugin-core/src/preview-server-plugin/plugin.ts` - Reads `rollupOptions.input` for server entry point

## What You Need to Do

1. Add runtime Vite version detection to `packages/start-plugin-core/src/utils.ts`:
   - Import the `vite` module
   - Check if `'rolldownVersion'` exists in the vite module (indicates Vite 8+)
   - Export a computed key `bundlerOptionsKey` that returns `'rolldownOptions'` for Vite 8+ or `'rollupOptions'` for Vite 7
   - Export a helper function `getBundlerOptions(build)` that reads `build.rolldownOptions` or `build.rollupOptions`

2. Update `packages/start-plugin-core/src/plugin.ts`:
   - Import the bundler utilities from `utils.ts`
   - Replace hardcoded `rollupOptions:` with computed `[bundlerOptionsKey]:` in client environment config
   - Replace hardcoded `rollupOptions:` with computed `[bundlerOptionsKey]:` in server environment config
   - Replace direct `build?.rollupOptions?.input` access with `getBundlerOptions(build)?.input` when reading server input

3. Update `packages/start-plugin-core/src/preview-server-plugin/plugin.ts`:
   - Import `getBundlerOptions` from `../utils`
   - Replace `serverEnv?.build.rollupOptions.input` with `getBundlerOptions(serverEnv?.build)?.input`

## Key Files

- `packages/start-plugin-core/src/utils.ts` - Add the detection utilities
- `packages/start-plugin-core/src/plugin.ts` - Update environment configs (~line 247 client, ~line 267 server)
- `packages/start-plugin-core/src/preview-server-plugin/plugin.ts` - Update server input reading (~line 30)

## Testing

After making changes, ensure:
- `pnpm nx run @tanstack/start-plugin-core:test:types` passes
- `pnpm nx run @tanstack/start-plugin-core:test:eslint` passes
- `pnpm nx run @tanstack/start-plugin-core:build` succeeds

## References

- Vite 8 Rolldown migration: `build.rollupOptions` is renamed to `build.rolldownOptions`
- The fix should be backward compatible with Vite 7 (use `rollupOptions` when Rolldown is not detected)
