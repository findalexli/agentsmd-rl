# Task: Add VM-level argument count check to Move VM

## Problem

The Move VM currently lacks direct validation of argument counts in its core execution path. When `execute_function` is called, it does not verify that the number of value arguments passed matches the function's signature. This check currently only happens at a higher layer (`ValueFrame::serialized_call`), which is a deserialization wrapper that serializes `MoveValue` to bytes and deserializes back.

Without this check in the VM itself, incorrect argument counts could potentially cause issues if code bypasses the adapter layer and calls the VM directly.

## Task

Add argument count validation directly in the Move VM's `execute_function` method.

### Key requirements:

1. **Value argument count check**: Before executing a function, verify that `args.len() != function.to_ref().parameters.len()`. If the counts don't match, return a `NUMBER_OF_ARGUMENTS_MISMATCH` error.

2. **Type argument count check**: Similarly, verify that `type_arguments.len() != function.to_ref().type_parameters().len()`. If the counts don't match, return an `INTERNAL_TYPE_ERROR` error.

3. **Update tests**: The existing unit tests in `function_arg_tests.rs` use `ValueFrame::serialized_call`. Convert these to call `execute_function_bypass_visibility` directly with `Value` objects instead of `MoveValue`, and add tests for type argument count mismatches.

## Files to modify

- `external-crates/move/crates/move-vm-runtime/src/execution/vm.rs` — Add the argument count checks
- `external-crates/move/crates/move-vm-runtime/src/unit_tests/function_arg_tests.rs` — Update tests to use direct VM calls and add type arg tests

## Expected behavior

After the fix, calling a function with the wrong number of arguments should return `NUMBER_OF_ARGUMENTS_MISMATCH` error, and calling with wrong number of type arguments should return `INTERNAL_TYPE_ERROR` error.

## Agent config references

- Root `CLAUDE.md`: Run tests with `cargo nextest run -p move-vm-runtime --lib -- function_arg_tests`
- Root `CLAUDE.md`: Always run `cargo xclippy` after finishing development
- Root `CLAUDE.md`: Use 10+ minute timeouts for Sui codebase compilation/tests

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo fmt (Rust formatter)`
