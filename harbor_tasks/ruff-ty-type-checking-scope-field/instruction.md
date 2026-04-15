# Remove per-scope TYPE_CHECKING tracking in ty

## Problem

The `Scope` struct currently stores a boolean `in_type_checking_block` field that tracks whether the scope was defined inside an `if TYPE_CHECKING:` block. This is redundant because the same information can be derived by checking ancestor scopes and their use-def maps for TYPE_CHECKING block ranges.

This redundant state adds unnecessary storage overhead per scope and complicates the semantic index builder. The information is already available via the `is_range_in_type_checking_block` mechanism on use-def maps.

## Expected Behavior

Refactor the TYPE_CHECKING detection to eliminate the per-scope boolean:

- The `Scope` struct should no longer store the `in_type_checking_block` field
- The `Scope` struct should no longer expose an `in_type_checking_block()` getter method
- The `is_in_type_checking_block` method on `SemanticIndex` should derive the information by checking ancestor scopes and their use-def maps, rather than reading a stored flag from the scope
- Any code that previously called `.in_type_checking_block()` directly on a scope must be updated to use the `SemanticIndex::is_in_type_checking_block` method instead
- All existing TYPE_CHECKING detection must continue to work correctly (cargo check, clippy, tests, fmt must all pass)

## Files to Look At

- `crates/ty_python_semantic/src/semantic_index/scope.rs` — The `Scope` struct definition
- `crates/ty_python_semantic/src/semantic_index.rs` — The `is_in_type_checking_block` method
- `crates/ty_python_semantic/src/semantic_index/builder.rs` — Where scopes are constructed
- `crates/ty_python_semantic/src/types/infer/builder/function.rs` — Caller that checks TYPE_CHECKING for function bodies
- `crates/ty_python_semantic/src/types/infer/builder/post_inference/overloaded_function.rs` — Caller that checks TYPE_CHECKING for overloaded functions
