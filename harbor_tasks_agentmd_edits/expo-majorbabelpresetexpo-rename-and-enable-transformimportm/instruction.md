# Promote `unstable_transformImportMeta` to stable in babel-preset-expo

## Problem

The `babel-preset-expo` package has an option called `unstable_transformImportMeta` that controls whether `import.meta` expressions are transformed to `globalThis.__ExpoImportMetaRegistry`. Currently this option defaults to `false` for client bundles and `true` only for server bundles. Since Expo never runs in a native ESM context that supports `import.meta`, many libraries break when they use `import.meta` in client code because the transform is off by default.

## Expected Behavior

- The option should be renamed from `unstable_transformImportMeta` to `transformImportMeta` (removing the unstable prefix) since it's ready for general use.
- The option should default to `true` for **all** environments (not just server), so `import.meta` is always transformed unless explicitly opted out.
- Error messages referencing the old option name should be updated.
- The package's README documentation should be updated to reflect the new option name, new default value, and remove the "at your own risk" warning.

## Files to Look At

- `packages/babel-preset-expo/src/index.ts` — preset entry point, option types and default logic
- `packages/babel-preset-expo/src/import-meta-transform-plugin.ts` — the transform plugin with error messages
- `packages/babel-preset-expo/build/` — compiled output (must stay in sync with source)
- `packages/babel-preset-expo/README.md` — documentation for all preset options
