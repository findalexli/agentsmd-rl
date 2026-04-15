# Fix Package Linkage in Move Unit Test Runner

## Problem

The Move unit test runner (`move-unit-test` crate) fails to compile due to API changes in the Move VM runtime. The `StoredPackage::from_modules_for_testing` API now requires a linkage context to be provided for proper package linkage during test execution.

The compilation error occurs because the test storage setup code in `external-crates/move/crates/move-unit-test/src/test_runner.rs` calls an API that no longer exists without linkage context. When running tests that involve multiple packages, proper linkage context is required to avoid module resolution failures.

## What You Need to Do

1. Fix the compilation error in `external-crates/move/crates/move-unit-test/src/test_runner.rs`
2. Ensure the linkage context is properly constructed from the package addresses available in the test storage setup
3. Make sure the `move-unit-test` crate compiles successfully with `cargo check -p move-unit-test`

## Key Information

- The file to modify: `external-crates/move/crates/move-unit-test/src/test_runner.rs`
- The issue involves the `StoredPackage` API which now requires linkage context
- The `move_vm_runtime` crate provides linkage context functionality through its shared module
- Linkage context needs to map package addresses appropriately for proper module resolution

## Verification

After your changes:
- The `move-unit-test` crate should compile successfully with `cargo check -p move-unit-test`
- The code should properly handle package linkage context
- The `cargo test -p move-unit-test` should pass

## Files to Modify

Only modify:
- `external-crates/move/crates/move-unit-test/src/test_runner.rs`

Do NOT modify any other files.
