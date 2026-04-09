# Remove per-scope TYPE_CHECKING tracking in ty

## Problem

The `Scope` struct in `crates/ty_python_semantic/src/semantic_index/scope.rs` currently stores a boolean `in_type_checking_block` field that tracks whether the scope was defined inside an `if TYPE_CHECKING:` block. This is redundant — the same information can be derived by walking up through ancestor scopes and checking their use-def maps for TYPE_CHECKING block ranges.

This redundant state adds unnecessary storage overhead per scope and requires the semantic index builder to thread the boolean through scope construction, when the information is already available via the existing `is_range_in_type_checking_block` mechanism on use-def maps.

## Expected Behavior

Remove the `in_type_checking_block` field from `Scope` and update all callers to use ancestor scope iteration with `is_range_in_type_checking_block` instead. The refactoring should be behavior-preserving — all existing TYPE_CHECKING detection must continue to work correctly.

Specifically:
- The `Scope` struct should no longer store this boolean
- The `Scope::new()` constructor should no longer accept this parameter
- The `SemanticIndexBuilder` should no longer pass the value
- The `is_in_type_checking_block` method on `SemanticIndex` should iterate through ancestor scopes
- All callers in the type inference builder (function handling and overloaded function checking) should use the updated approach

## Files to Look At

- `crates/ty_python_semantic/src/semantic_index/scope.rs` — The `Scope` struct definition and its methods
- `crates/ty_python_semantic/src/semantic_index.rs` — The `is_in_type_checking_block` method that needs to iterate ancestors
- `crates/ty_python_semantic/src/semantic_index/builder.rs` — Where scopes are constructed
- `crates/ty_python_semantic/src/types/infer/builder/function.rs` — Caller that checks TYPE_CHECKING for function bodies
- `crates/ty_python_semantic/src/types/infer/builder/post_inference/overloaded_function.rs` — Caller that checks TYPE_CHECKING for overloaded functions
