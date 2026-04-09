# Move VM Argument Checking

The Move VM runtime (`external-crates/move/crates/move-vm-runtime/src/execution/vm.rs`) is missing validation of argument counts when executing functions. This can lead to incorrect function execution.

## Problem

When a Move function is called via `execute_function`, the VM does not verify that:
1. The number of provided value arguments matches the function's parameter count
2. The number of provided type arguments matches the function's type parameter count

This missing validation should be caught and reported with appropriate error codes (`NUMBER_OF_ARGUMENTS_MISMATCH` and `INTERNAL_TYPE_ERROR` for type argument mismatches).

## Your Task

Add argument count validation in the `execute_function` method in `vm.rs` before the function execution. The validation should:

1. Check if `args.len()` matches `function.to_ref().parameters.len()` and return a `NUMBER_OF_ARGUMENTS_MISMATCH` error if they don't match
2. Check if `type_arguments.len()` matches `function.to_ref().type_parameters().len()` and return an `INTERNAL_TYPE_ERROR` if they don't match

Both error messages should include the expected and actual counts for debugging purposes.

## Relevant Files

- `external-crates/move/crates/move-vm-runtime/src/execution/vm.rs` - Main VM execution logic

## Testing

After implementing the fix, the following unit tests in `function_arg_tests.rs` should pass:
- Tests for argument count mismatches (too few, too many)
- Tests for type argument count mismatches

To run the tests:
```bash
cd external-crates/move/crates/move-vm-runtime
cargo test --lib function_arg
```

## Notes

- The error should be returned using `partial_vm_error!` macro and finished with `.finish(Location::Module(...))`
- You can reference the `StatusCode` enum for error types like `NUMBER_OF_ARGUMENTS_MISMATCH`
- The `function.to_ref()` provides access to the function metadata including `parameters` and `type_parameters()`
