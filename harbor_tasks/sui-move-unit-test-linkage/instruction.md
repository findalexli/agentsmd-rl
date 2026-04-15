# Fix Move Unit Test Runner Linkage Context

## Problem

The Move unit test runner fails to properly provide full linkage for packages during test setup, causing compilation errors when running tests that involve cross-package dependencies. The current implementation in `external-crates/move/crates/move-unit-test/src/test_runner.rs` creates `StoredPackage` instances without a proper `LinkageContext`, which is required for cross-package test execution.

## Required Fix

The `setup_test_storage` function must be updated to use linkage-aware package creation. The corrected implementation should contain the following specific elements:

### Import Requirements
- The import from `move_vm_runtime::shared` must include both `gas::GasMeter` and `linkage_context` using the pattern: `shared::{gas::GasMeter, linkage_context}`

### Linkage Context Creation
- A variable named `linkage_table` must be created that maps package addresses to themselves (identity mapping)
- The table should be constructed from the `packages` map keys using `packages.keys().copied()`
- A `LinkageContext` must be instantiated using `linkage_context::LinkageContext::new(linkage_table)`

### Package Creation
- The code must call `from_module_for_testing_with_linkage` instead of `from_modules_for_testing`
- The linkage context must be passed to each package creation via `linkage_context.clone()`

## Verification

After the fix:
1. `cargo check -p move-unit-test` must pass without errors
2. `cargo build -p move-unit-test --lib` must complete successfully
3. The implementation must include all the specific elements listed above
