# Move VM Argument Validation

The Move VM runtime has a gap in its execution path: it does not validate that the number of arguments provided when calling a function matches what the function expects. This causes functions to be invoked with incorrect argument counts, leading to unpredictable behavior or silent corruption.

## Problem

When `execute_function` in `external-crates/move/crates/move-vm-runtime/src/execution/vm.rs` is called, the VM proceeds directly to execution without checking whether:

1. The count of value arguments supplied matches the function's parameter count
2. The count of type arguments supplied matches the function's type parameter count

Without these checks, calling a function that expects 2 arguments with only 1 argument will attempt the call and produce undefined behavior, rather than failing fast with a clear error.

## Expected Behavior

The VM should reject calls where argument counts don't match, returning errors with appropriate `StatusCode` values:

- Value argument count mismatch → `NUMBER_OF_ARGUMENTS_MISMATCH`
- Type argument count mismatch → `INTERNAL_TYPE_ERROR`

The error messages should include both the expected and actual counts for debugging.

## Verification

After implementing the fix, the following tests in `function_arg_tests.rs` should pass:

**Value argument mismatches:**
- `expected_0_args_got_1` — calling a 0-arg function with 1 argument
- `expected_1_arg_got_0` — calling a 1-arg function with 0 arguments
- `expected_2_arg_got_1` — calling a 2-arg function with 1 argument
- `expected_2_arg_got_3` — calling a 2-arg function with 3 arguments

**Type argument mismatches:**
- `expected_1_ty_arg_got_0` — calling a generic function expecting 1 type arg with 0 type args
- `expected_1_ty_arg_got_2` — calling a generic function expecting 1 type arg with 2 type args
- `expected_0_ty_args_got_1` — calling a non-generic function with 1 type arg
- `expected_2_ty_args_got_1` — calling a generic function expecting 2 type args with 1
- `expected_2_ty_args_got_3` — calling a generic function expecting 2 type args with 3

**Happy paths:**
- `expected_0_args_got_0` — correct 0 arguments
- `expected_u64_got_u64` — correct 1 argument

Run with:
```bash
cd external-crates/move/crates/move-vm-runtime
cargo test --lib function_arg
```

## Notes

- The error codes (`NUMBER_OF_ARGUMENTS_MISMATCH`, `INTERNAL_TYPE_ERROR`) are defined in the `StatusCode` enum
- Use the `partial_vm_error!` macro to create errors, finished with `.finish(Location::Module(...))`
- The function metadata (parameter count, type parameter count) is accessible via `function.to_ref()`
