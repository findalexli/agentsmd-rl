# Task: Remove Unused Deserialization Functions

## Problem

The `move-core-types` crate contains several `simple_deserialize` methods that are no longer needed. These methods were previously used but have been superseded by `BoundedVisitor::deserialize_value`. This task involves removing these unused methods.

## Important Note

The `crates/sui-analytics-indexer/src/handlers/tables/event.rs` file **already uses** `BoundedVisitor::deserialize_value` at the base commit (it was fixed in a previous PR). You do NOT need to modify this file - it's already in the correct state.

Your task is to remove the now-unused methods from the following files.

## Files to Modify

### Primary Files

1. **`external-crates/move/crates/move-core-types/src/annotated_value.rs`**
   - Remove `MoveValue::simple_deserialize` method (lines ~184-187)
   - Remove `MoveStruct::simple_deserialize` method (lines ~268-271)
   - Remove `MoveVariant::simple_deserialize` method (lines ~324-326)
   - Remove the `use anyhow::Result as AResult;` import (it should be unused after removing these methods)
   - Remove the TODO comment about "annotated-visitor" if present

2. **`external-crates/move/crates/move-core-types/src/runtime_value.rs`**
   - Remove `MoveStruct::simple_deserialize` method
   - Remove `MoveVariant::simple_deserialize` method

### Test File

3. **`external-crates/move/crates/move-core-types/src/unit_tests/value_test.rs`**
   - The tests already use a helper function `deser_annotated_value` instead of the removed methods (this is already fixed at base)

## What the Methods Look Like

The methods to remove follow this pattern:

```rust
/// TODO (annotated-visitor): Port legacy uses of this method to `BoundedVisitor`.
pub fn simple_deserialize(blob: &[u8], ty: &SomeLayoutType) -> AResult<Self> {
    Ok(bcs::from_bytes_seed(ty, blob)?)
}
```

## Verification

After making these changes:
- `cargo check` in `external-crates/move/crates/move-core-types/` should pass
- `cargo check --tests` in the same directory should pass
- The `anyhow::Result as AResult` import should be removed (it becomes unused)

## Important Notes

- Do NOT just add `#[allow(dead_code)]` or suppress warnings - actually remove the unused code
- Do NOT modify `event.rs` - it's already correct at base commit
- The TODO comments mentioning "annotated-visitor" should be removed along with the methods
