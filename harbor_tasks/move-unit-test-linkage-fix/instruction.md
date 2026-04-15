# Fix Package Linkage in Move Unit Test Runner

## Problem

The Move unit test runner crashes when running unit tests that involve cross-package dependencies. When modules in one package need to reference modules in another package, the VM runtime fails because the stored packages lack proper linkage context.

## What You Need to Do

Modify the `setup_test_storage` function in `external-crates/move/crates/move-unit-test/src/test_runner.rs` to properly initialize package linkage.

The current implementation creates StoredPackage instances without linkage context. This causes linkage errors when tests have cross-package dependencies.

### Requirements

1. **Import the linkage context module**: The `linkage_context` module must be imported from `move_vm_runtime::shared` alongside the existing `gas::GasMeter` import.

2. **Create a linkage table**: Before iterating over packages, construct a linkage table that maps each package address to itself (identity mapping) using the keys of the `packages` BTreeMap. The table format should be a BTreeMap where each address maps to itself.

3. **Create a LinkageContext**: Instantiate a `LinkageContext` using the linkage table. The `LinkageContext::new()` constructor requires a valid table and will return `Ok` on success.

4. **Update package loading**: Change the package creation to use a method that accepts linkage context, passing the linkage context (cloned) as a parameter along with the address and modules. The old method that doesn't accept linkage context should no longer be used in this function.

### Verification

After making changes:
1. Run `cargo check -p move-unit-test` to verify the code compiles
2. The changes should only affect the `setup_test_storage` function
3. No other parts of the codebase should need modification for this fix
