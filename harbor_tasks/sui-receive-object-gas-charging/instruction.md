# Add per-byte gas charging to receive_object native function

## Problem

The `receive_object` Move native function in Sui currently only charges a base cost. It doesn't account for the size of the object being received or the size of its type, which means large objects cost the same as small ones. This creates non-uniform gas pricing that doesn't reflect actual resource usage.

## Goal

Add per-byte gas charging to the `receive_object` native function, similar to how other transfer operations in Sui charge based on object size.

## What to implement

### 1. Protocol config (`crates/sui-protocol-config/src/lib.rs`)

Add two new cost parameter fields to `ProtocolConfig`:
- A field for per-byte object size charging
- A field for per-byte type size charging

For protocol version 119, set the per-byte object cost to `Some(1)` and the per-byte type cost to `Some(2)`.

### 2. Native cost params (`sui-execution/latest/sui-move-natives/src/transfer.rs`)

Add two new fields to `TransferReceiveObjectInternalCostParams` for internal gas cost tracking.

Add gas charging logic within `receive_object_internal` that:
- Charges based on the type size before processing
- Charges based on the object size before returning

Import `SizeConfig` and `ValueView` from `move_vm_runtime::shared::views` for size calculations.

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
