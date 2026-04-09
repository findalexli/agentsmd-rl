# Fix Package Linkage in Move Unit Test Runner

## Problem

The Move unit test runner (`move-unit-test` crate) is not properly handling package linkage when setting up test storage. This causes issues when running tests that involve multiple packages - specifically, the packages don't have proper linkage context which can lead to module resolution failures during test execution.

## Location

The issue is in the test storage setup function in:

```
external-crates/move/crates/move-unit-test/src/test_runner.rs
```

Look for the `setup_test_storage` function, specifically around where `StoredPackage` instances are created from modules.

## What Needs to Change

The current code creates `StoredPackage` instances without proper linkage context. You need to:

1. Import `linkage_context` from `move_vm_runtime::shared` alongside the existing imports
2. Create a linkage table that maps package addresses to themselves
3. Create a `LinkageContext` from this linkage table
4. Use `StoredPackage::from_module_for_testing_with_linkage` instead of `StoredPackage::from_modules_for_testing`, passing the linkage context

## Key Details

- The linkage table should be constructed from the `packages` map keys (the package addresses)
- Each address should map to itself in the linkage table (identity mapping)
- The linkage context needs to be cloned when passed to each package creation

## Verification

After your changes:
- The `move-unit-test` crate should compile successfully with `cargo check -p move-unit-test`
- The code should properly import and use `LinkageContext`
- The `from_module_for_testing_with_linkage` function should be called instead of `from_modules_for_testing`

## Files to Modify

Only modify:
- `external-crates/move/crates/move-unit-test/src/test_runner.rs`

Do NOT modify any other files.
