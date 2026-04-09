# Fix Move Unit Test Runner Linkage Context

## Problem

The Move unit test runner in `external-crates/move/crates/move-unit-test/src/test_runner.rs` is not providing full linkage for packages during test setup. This causes issues when running tests that involve cross-package dependencies.

## Your Task

Fix the `setup_test_storage` function in `test_runner.rs` to properly provide linkage context when creating `StoredPackage` instances.

## Key Details

1. The function currently creates packages without proper linkage context
2. You need to:
   - Import `linkage_context` from `move_vm_runtime::shared`
   - Create a `LinkageContext` with an identity mapping (each address maps to itself)
   - Use `from_module_for_testing_with_linkage` instead of `from_modules_for_testing`
   - Pass the linkage context when creating each package

## Files to Modify

- `external-crates/move/crates/move-unit-test/src/test_runner.rs`

## Hints

- Look at the `setup_test_storage` function and how packages are created
- The `linkage_context::LinkageContext::new` function takes a mapping from address to address
- The packages are stored in a `BTreeMap<AccountAddress, Vec<CompiledModule>>`
- You'll need to clone the linkage context for each package creation

## Verification

After your fix:
1. `cargo check -p move-unit-test` should pass
2. The code should use the new linkage-aware package creation method
