# Fix Package Linkage in Move Unit Test Runner

## Problem

The Move unit test runner is not correctly handling package linkage when setting up test storage. When running unit tests that involve multiple packages with cross-package dependencies, the test runner fails to provide proper linkage context to the VM runtime.

## Location

The issue is in the `setup_test_storage` function within:
- `external-crates/move/crates/move-unit-test/src/test_runner.rs`

## What You Need to Do

The `setup_test_storage` function iterates over packages and creates `StoredPackage` instances for testing. Currently, it creates packages without proper linkage context, which causes issues when modules in one package need to reference modules in another package.

You need to:

1. **Import the linkage context module**: Add `linkage_context` to the imports from `move_vm_runtime::shared`.

2. **Create a linkage table**: Before the loop that creates `StoredPackage` instances, construct a linkage table that maps each package address to itself (identity mapping). This table should be built from the keys of the `packages` BTreeMap:
   ```rust
   let linkage_table = packages.keys().copied().map(|addr| (addr, addr)).collect();
   ```

3. **Create a LinkageContext**: Use the linkage table to create a `LinkageContext`:
   ```rust
   let linkage_context = linkage_context::LinkageContext::new(linkage_table).unwrap();
   ```

4. **Update StoredPackage creation**: Modify the loop that creates `StoredPackage` instances to:
   - Use `StoredPackage::from_module_for_testing_with_linkage` instead of `from_modules_for_testing`
   - Pass the `linkage_context` (cloned) as a parameter along with the address and modules

## Key Points

- The `LinkageContext` type is located in `move_vm_runtime::shared::linkage_context`
- The linkage table is a `BTreeMap` where each package address maps to itself
- The `StoredPackage::from_module_for_testing_with_linkage` method takes three parameters: address, linkage_context, and modules
- Make sure to clone the linkage_context when passing it to each package creation

## Verification

After making changes:
1. Run `cargo check -p move-unit-test` to verify the code compiles
2. The changes should only affect the `setup_test_storage` function
3. No other parts of the codebase should need modification for this fix
