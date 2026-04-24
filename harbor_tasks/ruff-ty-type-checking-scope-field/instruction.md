# Remove per-scope TYPE_CHECKING tracking in ty_python_semantic

## Problem

The `Scope` struct in `crates/ty_python_semantic/src/semantic_index/scope.rs` currently stores a boolean field `in_type_checking_block` that tracks whether the scope was defined inside an `if TYPE_CHECKING:` block. This field is redundant because the same information can be derived by querying ancestor scopes and their use-def maps.

Additionally, some callers in `function.rs` and `overloaded_function.rs` directly access this per-scope field via a getter method, rather than going through the proper semantic index interface.

## Symptom

Running `cargo check -p ty_python_semantic` reports that the `in_type_checking_block` field on `Scope` is unused or redundant. The `SemanticIndex` already exposes `is_range_in_type_checking_block` which can be used to determine if a position falls within a TYPE_CHECKING block by checking the use-def map of any scope in the parent chain.

The codebase needs to be cleaned up to remove this redundant per-scope state and ensure all access to TYPE_CHECKING block detection goes through the semantic index's `is_in_type_checking_block` method.

## Expected Behavior

All existing TYPE_CHECKING detection must continue to work correctly. Any code that checks whether the current position is inside a TYPE_CHECKING block should produce the same results as before. Specifically:

- `cargo check -p ty_python_semantic` must pass without warnings about unused fields
- `cargo clippy -p ty_python_semantic --all-targets --all-features -- -D warnings` must pass
- `cargo test -p ty_python_semantic --lib` must pass
- `cargo fmt -- --check` must pass

## Files to Look At

- `crates/ty_python_semantic/src/semantic_index/scope.rs` — The `Scope` struct definition
- `crates/ty_python_semantic/src/semantic_index.rs` — The `is_in_type_checking_block` method
- `crates/ty_python_semantic/src/semantic_index/builder.rs` — Where scopes are constructed
- `crates/ty_python_semantic/src/types/infer/builder/function.rs` — Code that checks TYPE_CHECKING for function bodies
- `crates/ty_python_semantic/src/types/infer/builder/post_inference/overloaded_function.rs` — Code that checks TYPE_CHECKING for overloaded functions