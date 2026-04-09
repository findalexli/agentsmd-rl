# Harden Sui Move Native Functions with Safe Macros

## Problem

The Sui Move VM's native functions currently use Rust's standard `.unwrap()`, `.expect()`, `assert!`, and `assert_eq!` macros in many places. When these operations fail, they cause the entire validator process to panic. This is undesirable in a blockchain environment where:

1. A malformed transaction could crash a validator
2. The VM should gracefully return errors to users instead of crashing
3. Different code paths may have invariant violations that should be recoverable

The `move-binary-format` crate provides `safe_unwrap!`, `safe_unwrap_err!`, and `safe_assert!` macros that convert failures into proper VM errors (`PartialVMError` with `UNKNOWN_INVARIANT_VIOLATION_ERROR`) instead of panicking.

## What Needs to Change

### 1. Add `safe_assert_eq!` macro

The `move-binary-format/src/lib.rs` file needs a new `safe_assert_eq!` macro similar to `safe_assert!` but for equality assertions. It should:
- Take two expressions to compare
- If they differ, create a `PartialVMError` with message showing both values
- Panic in debug mode, return error in release mode

### 2. Fix `safe_unwrap_err!` macro

The existing `safe_unwrap_err!` macro in `move-binary-format/src/lib.rs` uses unqualified paths for `PartialVMError` and `StatusCode`. These should use fully qualified paths (`move_binary_format::errors::PartialVMError`, `move_core_types::vm_status::StatusCode`) to work correctly from external crates.

### 3. Update Native Functions

All files in `sui-execution/latest/sui-move-natives/src/` need to replace panicking operations with safe macros:

- Replace `.unwrap()` on `Option` values with `safe_unwrap!`
- Replace `.unwrap()` on `Result` values with `safe_unwrap_err!`
- Replace `.expect("...")` with `safe_unwrap_err!`
- Replace `assert!(...)` with `safe_assert!`
- Replace `assert_eq!(...)` with `safe_assert_eq!`

### 4. Handle Error Propagation

Some functions that previously returned `Value` or other types directly may now need to return `PartialVMResult<T>` because operations that could panic (like `Vector::pack()`) now return `Result`. Update these function signatures and propagate errors with `?`.

## Files to Modify

**Core macro changes:**
- `external-crates/move/crates/move-binary-format/src/lib.rs`

**Native function files:**
- `sui-execution/latest/sui-move-natives/src/accumulator.rs`
- `sui-execution/latest/sui-move-natives/src/address.rs`
- `sui-execution/latest/sui-move-natives/src/config.rs`
- `sui-execution/latest/sui-move-natives/src/dynamic_field.rs`
- `sui-execution/latest/sui-move-natives/src/event.rs`
- `sui-execution/latest/sui-move-natives/src/funds_accumulator.rs`
- `sui-execution/latest/sui-move-natives/src/lib.rs`
- `sui-execution/latest/sui-move-natives/src/test_scenario.rs`
- `sui-execution/latest/sui-move-natives/src/test_utils.rs`
- `sui-execution/latest/sui-move-natives/src/transfer.rs`
- `sui-execution/latest/sui-move-natives/src/tx_context.rs`
- `sui-execution/latest/sui-move-natives/src/types.rs`
- `sui-execution/latest/sui-move-natives/src/crypto/group_ops.rs`
- `sui-execution/latest/sui-move-natives/src/crypto/hmac.rs`

## Verification

After your changes:
1. `cargo check -p move-binary-format` should succeed
2. `cargo check -p sui-move-natives` should succeed
3. All uses of `.unwrap()`, `.expect()`, `assert!`, and `assert_eq!` in native functions should be replaced with safe macros
4. Function signatures that use operations that can now return errors should return `PartialVMResult<T>`

## Reference

Look at existing `safe_unwrap!`, `safe_unwrap_err!`, and `safe_assert!` macro definitions in `move-binary-format/src/lib.rs` for the pattern to follow.
