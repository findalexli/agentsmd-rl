# Fix `gradio cc build` crash when example export is missing

## Problem

When a custom component does not export an `./example` field in its `package.json`, running `gradio cc build` crashes with a `TypeError`. The error occurs because the build pipeline unconditionally accesses a property on `./example`, which throws when `./example` is not defined.

The same crash happens if `./example` is explicitly set to `null`.

## Expected Behavior

1. `gradio cc build` should succeed for custom components that do not have an `./example` export in their `package.json`. The exports array construction must not crash when `./example` is absent or null.

2. When `./example` is absent from `package.json` exports, the resulting exports array should contain exactly **1 entry** (the component entry only).

3. When `./example` IS present in `package.json` exports, the resulting exports array should contain exactly **2 entries** (the component entry plus the example entry).

4. The build implementation must still contain real build logic including:
   - A call to `build(` (the Vite build function)
   - A reference to `pkg.exports`

5. The fix must pass the repository's formatting check: `pnpm format:check`

## Files to Look At

- The build pipeline for custom components in `js/preview/src/` — contains the exports array construction that crashes
- The dev server equivalent that may be useful as a reference for how similar logic is handled elsewhere
