# Task: Remove Unused Deserialization Functions

## Problem

The Move core types crate contains several `simple_deserialize` methods that are no longer needed or used. These should be removed and any call sites updated to use the appropriate alternatives.

## Affected Files

The following files need to be modified:

1. **external-crates/move/crates/move-core-types/src/annotated_value.rs**
   - Contains `simple_deserialize` methods on `MoveValue`, `MoveStruct`, and `MoveVariant`
   - These methods are marked with TODO comments indicating they should be ported to `BoundedVisitor`

2. **external-crates/move/crates/move-core-types/src/runtime_value.rs**
   - Contains `simple_deserialize` methods on `MoveStruct` and `MoveVariant`

3. **external-crates/move/crates/move-core-types/src/unit_tests/value_test.rs**
   - Contains tests that currently use `A::MoveValue::simple_deserialize()`
   - Needs to be updated to use an alternative approach

4. **crates/sui-analytics-indexer/src/handlers/tables/event.rs**
   - Currently uses `MoveValue::simple_deserialize()` to deserialize event contents
   - Should be updated to use `BoundedVisitor::deserialize_value()` instead

## Requirements

1. Remove all `simple_deserialize` methods from `annotated_value.rs` and `runtime_value.rs`
2. Remove any unused imports that were only used by these methods
3. Update `event.rs` to use `BoundedVisitor::deserialize_value()` from `sui_types::object::bounded_visitor` instead of `MoveValue::simple_deserialize()`
4. Update `value_test.rs` tests to use a helper function named `deser_annotated_value` for deserializing annotated values
5. Ensure all tests in the `move-core-types` crate pass after the changes
6. Ensure the code compiles without warnings
