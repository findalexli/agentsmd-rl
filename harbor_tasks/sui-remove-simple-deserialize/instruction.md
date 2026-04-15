# Task: Remove Unused Deserialization Functions

## Problem

The `move-core-types` crate contains deprecated `simple_deserialize` methods that are no longer needed. These methods were previously used but have been superseded by `BoundedVisitor::deserialize_value`. The code using `BoundedVisitor::deserialize_value` (in `event.rs`) was already fixed in a previous PR. The remaining unused methods should now be removed.

After these methods are removed, the `move-core-types` crate should compile cleanly with `cargo check`, `cargo build`, `cargo clippy`, and `cargo test`.

## What to Remove

The `simple_deserialize` method appears in several `impl` blocks in two files. These deprecated methods should be removed:

**In `external-crates/move/crates/move-core-types/src/annotated_value.rs`:**
- `MoveValue::simple_deserialize` method
- `MoveStruct::simple_deserialize` method
- `MoveVariant::simple_deserialize` method

**In `external-crates/move/crates/move-core-types/src/runtime_value.rs`:**
- `MoveStruct::simple_deserialize` method
- `MoveVariant::simple_deserialize` method

The import `use anyhow::Result as AResult;` in `annotated_value.rs` should also be removed, as it was only used by these methods and will become unused after their removal.

## Files You Should NOT Modify

- `crates/sui-analytics-indexer/src/handlers/tables/event.rs` — This file already uses `BoundedVisitor::deserialize_value` and is already correct at the base commit.

## Verification

After making these changes:
- `cargo check` in `external-crates/move/crates/move-core-types/` should pass
- `cargo check --tests` in the same directory should pass
- `cargo clippy -p move-core-types --all-targets` should pass
- `cargo test -p move-core-types --lib` should pass
- `cargo build -p move-core-types --all-targets` should pass

## Important Notes

- Do NOT just add `#[allow(dead_code)]` or suppress warnings — actually remove the unused code
- Do NOT modify `event.rs` — it's already correct at base commit