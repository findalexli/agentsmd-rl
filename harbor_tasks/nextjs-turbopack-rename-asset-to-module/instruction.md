# Rename SingleModuleReference::asset to SingleModuleReference::module

## Problem

In `turbopack/crates/turbopack-core/src/reference/mod.rs`, the `SingleModuleReference` struct has a field named `asset` that holds a `ResolvedVc<Box<dyn Module>>`. The field name `asset` is misleading — the type it stores is `Module`, not a generic asset. There is also a getter method `asset()` and a constructor `new(asset, ...)` that perpetuate this naming inconsistency.

This naming mismatch between the field name (`asset`) and the type it actually holds (`Module`) makes the code harder to understand and inconsistent with the rest of the codebase, where similar reference types use field names that match their semantic purpose.

## Expected Behavior

The field, constructor parameter, and internal references should use the name `module` to match the actual type stored. The old `asset()` getter should be removed since it is no longer needed.

## Files to Look At

- `turbopack/crates/turbopack-core/src/reference/mod.rs` — contains the `SingleModuleReference` struct definition and its implementations
