# Remove unused `all_definitely_bound` attribute from type inference

## Problem

The type inference builder in `ty_python_semantic` contains an `all_definitely_bound` boolean attribute that tracks whether all places in an expression are definitely bound. This attribute was rendered unused by a previous refactoring — it is still written to and read, but its value no longer influences any observable behavior. It is dead code that adds unnecessary complexity to the inference system.

The field exists in two locations:
- `ExpressionInferenceExtra` struct
- `TypeInferenceBuilder` struct

Both the field declarations and all logic that sets or reads the field should be removed.

## Expected Behavior

After removing the dead code, the crate should compile cleanly with no warnings. All existing type inference behavior should be preserved.

## Files to Look At

- `crates/ty_python_semantic/src/types/infer.rs` — contains the `ExpressionInferenceExtra` struct with the dead field
- `crates/ty_python_semantic/src/types/infer/builder.rs` — contains the `TypeInferenceBuilder` struct with the dead field and all related logic

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`
