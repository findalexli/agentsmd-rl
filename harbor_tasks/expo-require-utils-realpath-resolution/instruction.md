# Fix Module Resolution for Symlinked Paths in @expo/require-utils

## Problem

When using `evalModule` or `compileModule` from `@expo/require-utils`, module resolution fails when the input filename is a symlinked path. This is particularly problematic with pnpm and other package managers that use symlinks extensively.

### Symptom

Given a symlinked path like:
```
node_modules/expo/react-native.config.js -> .pnpm/expo@version/node_modules/expo/react-native.config.js
```

When `evalModule` is called with this symlinked path, internal module resolution (like requiring `expo-modules-autolinking/exports`) fails with `MODULE_NOT_FOUND` because the `Module._nodeModulePaths` are computed against the unresolved symlink path instead of the real path.

## Required Behavior

The implementation must ensure that:

1. **Module resolution works correctly for symlinked paths** - When a file path is a symlink, the `node_modules` lookup should use the actual filesystem location that the symlink resolves to, not the symlink path itself.

2. **Symlink resolution must happen before computing module paths** - The module path resolution must consider the real path of the file, not just its location in the symlink tree.

3. **Error handling for non-existent paths** - If a file doesn't exist but its parent directory does, resolution should continue gracefully rather than throwing an error.

4. **Existing API surface must be preserved** - The public API (`evalModule`, `compileModule`, `loadModule`) must maintain their current signatures and behavior for non-symlinked paths.

## Constraints

- The module path resolution must use the real filesystem path, not the symlink path
- The code must handle `ENOENT` errors gracefully for paths that don't exist
- No new dependencies may be added to the package

## Files to Modify

- `packages/@expo/require-utils/src/load.ts` - Add symlink resolution for module paths

The build files (`build/load.js`, `build/load.js.map`) will be regenerated during the build process.

## Reference

See the Node.js source for how module paths are computed:
https://github.com/nodejs/node/blob/ff080948666f28fbd767548d26bea034d30bc277/lib/internal/modules/cjs/loader.js#L767
