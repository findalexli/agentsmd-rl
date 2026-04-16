# Fix Module Resolution for Symlinked Paths in @expo/require-utils

## Problem

When using `evalModule` or `compileModule` from `@expo/require-utils`, module resolution fails when the input filename is a symlinked path. This is particularly problematic with pnpm and other package managers that use symlinks extensively.

### Symptom

Given a symlinked path like:
```
node_modules/expo/react-native.config.js -> .pnpm/expo@version/node_modules/expo/react-native.config.js
```

When `evalModule` is called with this symlinked path, internal module resolution (like requiring `expo-modules-autolinking/exports`) fails with `MODULE_NOT_FOUND` because the `Module._nodeModulePaths` are computed against the unresolved symlink path instead of the real path.

## Required Implementation

The fix must implement the following specific behavior:

1. **Create a helper function named `toRealDirname`** that:
   - Takes a file path string as input
   - Uses `fs.realpathSync` to resolve any symlinks in the path
   - Returns the directory name of the resolved path
   - Handles `ENOENT` errors gracefully: when the file doesn't exist, try resolving the directory instead of the file

2. **Modify the `compileModule` function** to:
   - Call `toRealDirname(filename)` to get a `basePath` variable
   - Pass this `basePath` to `Module._nodeModulePaths(basePath)` instead of `path.dirname(filename)`

3. **Error handling requirements**:
   - If `realpathSync` fails with `ENOENT` (file doesn't exist), resolve the directory instead
   - If resolving fails with other errors, return the original directory unchanged

## Constraints

- The function `toRealDirname` must be present in the file
- The variable `basePath` must be used when calling `Module._nodeModulePaths`
- The code must handle `ENOENT` errors in a try-catch block within `toRealDirname`

## Files to Modify

- `packages/@expo/require-utils/src/load.ts` - Add realpath resolution

The build files (`build/load.js`, `build/load.js.map`) will be regenerated during the build process.

## Reference

See the Node.js source for how module paths are computed:
https://github.com/nodejs/node/blob/ff080948666f28fbd767548d26bea034d30bc277/lib/internal/modules/cjs/loader.js#L767
