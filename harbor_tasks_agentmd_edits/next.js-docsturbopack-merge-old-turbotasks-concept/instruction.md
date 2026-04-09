# Turbopack chunking: split app code by monorepo package name

## Problem

Currently, Turbopack's chunking only splits app code by folder. When app code is organized in a monorepo structure (e.g., under `packages/`), it should be split by package name instead, similar to how vendor code is split by `node_modules` package name.

## Expected Behavior

The `package_name()` function in `turbopack/crates/turbopack-core/src/chunk/chunking/dev.rs` should recognize monorepo package paths (following the pattern `/packages/{package-name}`) in addition to the existing `node_modules` pattern. This enables better code splitting for monorepo setups.

For example:
- `/project/packages/ui/components/Button.js` → package name should be `ui`
- `/project/packages/@scope/utils/index.js` → package name should be `@scope/utils`

The app chunk splitting logic should use `package_name_split()` instead of `folder_split()` to take advantage of this package detection.

## Files to Look At

- `turbopack/crates/turbopack-core/src/chunk/chunking/dev.rs` — contains the chunking logic and `package_name()` function

## Implementation Notes

The `package_name()` function currently uses a regex to extract package names from `/node_modules/` paths. You need to:

1. Add a second regex for `/packages/` paths (monorepo convention)
2. Check node_modules pattern first, then fall back to monorepo pattern
3. Update `app_vendors_split()` to call `package_name_split()` for app chunk items instead of `folder_split()`
4. Update the doc comment for `package_name_split()` to mention monorepo packages
