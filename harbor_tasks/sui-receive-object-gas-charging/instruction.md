# Update charging around receive to be more uniform

## Problem

The `receive_object` Move native function in Sui currently only charges a base cost. It doesn't account for the size of the object being received or the size of its type, which means large objects cost the same as small ones. This creates non-uniform gas pricing that doesn't reflect actual resource usage.

## What needs to change

You need to add **per-byte gas charging** to the `receive_object` native function, similar to how other transfer operations charge based on object size.

## Relevant files

1. **`crates/sui-protocol-config/src/lib.rs`** - Add new cost parameters:
   - `transfer_receive_object_cost_per_byte: Option<u64>`
   - `transfer_receive_object_type_cost_per_byte: Option<u64>`
   - Set these to `Some(1)` and `Some(2)` respectively for protocol version 119

2. **`sui-execution/latest/sui-move-natives/src/transfer.rs`** - Update the native function implementation:
   - Add new fields to `TransferReceiveObjectInternalCostParams`
   - Import `SizeConfig` and `ValueView` from `move_vm_runtime::shared::views`
   - Add gas charging based on `child_ty.size()` before processing
   - Add gas charging based on `child.abstract_memory_size()` before returning

3. **`sui-execution/latest/sui-move-natives/src/lib.rs`** - Wire up the new protocol config values to the native cost params

4. **Snapshot files** - Update the protocol config test snapshots to include the new fields

## Expected behavior

After your changes:
- The protocol config should have the new cost fields
- The native function should charge gas proportional to both the type size and object size
- All existing tests should pass
- The code should compile without errors

## Hints

- Look at how other transfer operations (like `transfer_share_object`) charge per-byte costs for reference
- The `native_charge_gas_early_exit!` macro is used to charge gas within native functions
- Use `child_ty.size()?` for the type size calculation
- Use `child.abstract_memory_size(&SizeConfig {...})?` for the object size calculation
- Don't forget to update the snapshot files after making changes (use `cargo insta test -p sui-protocol-config --accept`)
