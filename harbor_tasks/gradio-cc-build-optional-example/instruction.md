# Fix `gradio cc build` crash when example export is missing

## Problem

When a custom component does not export an `./example` field in its `package.json`, running `gradio cc build` crashes with a `TypeError`. The error occurs because the build pipeline unconditionally accesses `pkg.exports["./example"].gradio`, which throws when `./example` is not defined.

The same crash happens if `./example` is explicitly set to `null`.

## Expected Behavior

`gradio cc build` should succeed for custom components that do not have an `./example` export in their `package.json`. The example entry should only be included in the build when it exists.

## Files to Look At

- `js/preview/src/build.ts` — The build pipeline for custom components; contains the `make_build` function and the exports array construction that crashes.
- `js/preview/src/dev.ts` — The dev server equivalent that may be useful as a reference for how similar logic is handled elsewhere.
