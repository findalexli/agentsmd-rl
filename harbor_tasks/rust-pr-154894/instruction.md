# Task: Refactor mplace<->ptr conversion functions

## Problem

The Rust compiler's interpreter (CTFE/Miri) has two functions in `compiler/rustc_const_eval/src/interpret/place.rs` whose names don't accurately describe their behavior:

1. `ref_to_mplace` - The name suggests it only works with references (`&T` / `&mut T`), but the function actually works with any pointer type (`*const T` / `*mut T`).

2. `mplace_to_ref` - Similarly, the name suggests it produces references, but it actually produces raw pointers.

The naming is misleading because these functions handle any pointer type (thin or wide), not just references. This makes the code harder to understand and maintain.

## What You Need To Do

Fix the misleading function names in `compiler/rustc_const_eval/src/interpret/place.rs`:

1. The function currently called `ref_to_mplace` should be renamed to clearly indicate it handles immediate pointer values (pointers passed directly, not stored in memory), not just references.

2. The function currently called `mplace_to_ref` should be renamed to clearly indicate it produces pointer values, not references. Additionally, add a parameter that lets callers specify the pointer type to create; when not provided, default to `*mut T` for backward compatibility.

## Files to Update

After renaming, update all callers in these files:
- `compiler/rustc_const_eval/src/const_eval/machine.rs`
- `compiler/rustc_const_eval/src/const_eval/type_info.rs`
- `compiler/rustc_const_eval/src/const_eval/type_info/adt.rs`
- `compiler/rustc_const_eval/src/interpret/call.rs`
- `compiler/rustc_const_eval/src/interpret/intrinsics.rs`
- `compiler/rustc_const_eval/src/interpret/validity.rs`
- `src/tools/miri/src/borrow_tracker/stacked_borrows/mod.rs`
- `src/tools/miri/src/borrow_tracker/tree_borrows/mod.rs`
- `src/tools/miri/src/shims/panic.rs`

## Documentation

Update the doc comments on the functions to clarify they work with pointers (thin or wide), not just references, and document the new parameter behavior.

## Verification

Your changes should:
1. Remove all occurrences of the old function names
2. Have all callers using the new function names
3. Include a pointer type parameter in the renamed `mplace_to_*` function (the parameter type should be `Option<Ty<'tcx>>`)
4. Update all relevant documentation