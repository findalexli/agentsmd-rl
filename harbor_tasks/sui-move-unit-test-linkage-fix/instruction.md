# Fix Package Linkage in Move Unit Test Runner

## Problem

The Move unit test runner (`move-unit-test` crate) fails to compile due to API changes in the Move VM runtime. When running `cargo check -p move-unit-test`, the compilation fails because the test storage setup code calls an API that no longer exists in its current form.

The error relates to how `StoredPackage` is constructed in `external-crates/move/crates/move-unit-test/src/test_runner.rs`. The current implementation does not provide the linkage context that the new API requires for proper package linkage during test execution.

## What You Need to Do

1. Identify why `cargo check -p move-unit-test` fails
2. Find the correct API in the `move_vm_runtime` crate that provides the required linkage context functionality
3. Update the code in `external-crates/move/crates/move-unit-test/src/test_runner.rs` to use the proper API that accepts linkage context
4. Verify the fix by running `cargo check -p move-unit-test` successfully

## Hint

The `move_vm_runtime::shared` module provides functionality for creating linkage context. Look for APIs in the `StoredPackage` family that accept linkage context parameters. The compilation error will indicate which function signature is expected.

## Verification

After your changes:
- `cargo check -p move-unit-test` must succeed
- `cargo test -p move-unit-test` must pass
- `cargo clippy -p move-unit-test` must pass
- `cargo fmt --check` must pass in the move crates directory
