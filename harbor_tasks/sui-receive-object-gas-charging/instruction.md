# Add per-byte gas charging to receive_object native function

## Problem

The `receive_object` Move native function in Sui currently only charges a base cost. It doesn't account for the size of the object being received or the size of its type, which means large objects cost the same as small ones. This creates non-uniform gas pricing that doesn't reflect actual resource usage.

## Goal

Add per-byte gas charging to the `receive_object` native function, similar to how other transfer operations in Sui charge based on object size.

## What to implement

### 1. Protocol config (`crates/sui-protocol-config/src/lib.rs`)

Add two new cost parameter fields to `ProtocolConfig` for per-byte charging:
- `transfer_receive_object_cost_per_byte: Option<u64>` — for object size based charging
- `transfer_receive_object_type_cost_per_byte: Option<u64>` — for type size based charging

For protocol version 119, set the per-byte costs to:
- `transfer_receive_object_cost_per_byte = Some(1)`
- `transfer_receive_object_type_cost_per_byte = Some(2)`

### 2. Native cost params (`sui-execution/latest/sui-move-natives/src/transfer.rs`)

Extend the `TransferReceiveObjectInternalCostParams` struct with new fields for internal gas cost tracking:
- `transfer_receive_object_internal_cost_per_byte: InternalGas`
- `transfer_receive_object_internal_type_cost_per_byte: InternalGas`

Add gas charging logic within `receive_object_internal` that:
- Charges based on the type size (using `child_ty.size()`) before processing
- Charges based on the object size (using `abstract_memory_size` with `SizeConfig`) before returning

Import the necessary types from `move_vm_runtime::shared::views` for size calculations.

### 3. Wire up protocol config (`sui-execution/latest/sui-move-natives/src/lib.rs`)

Populate the new native cost params from protocol config values.

### 4. Snapshot updates

Run `cargo insta test -p sui-protocol-config --accept` to update test snapshots.

## Verification

After changes:
- `cargo check -p sui-protocol-config` passes
- `cargo check -p sui-move-natives-latest` passes
- `cargo test -p sui-protocol-config` passes
- `cargo test -p sui-move-natives-latest` passes
- All other cargo checks (clippy, fmt, doc, xlint, etc.) pass

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo fmt (Rust formatter)`
