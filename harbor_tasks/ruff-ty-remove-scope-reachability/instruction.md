# Remove redundant per-scope reachability tracking from ty semantic index

## Problem

The ty type checker's semantic index maintains redundant reachability tracking. The `is_scope_reachable` method in `semantic_index.rs` performs recursive scope-level reachability checks by walking parent scopes. The `Scope` struct in `scope.rs` carries a dedicated `reachability` field that is stored during scope construction and used by `is_scope_reachable`.

This per-scope tracking is unnecessary because scope reachability can be determined by walking ancestor scopes and examining their use-def maps directly. The redundancy creates maintenance burden and complexity.

Additionally, the IDE type hierarchy code in `ide_support.rs` has a reachability-related bug: when iterating over class definitions to build the subtype hierarchy, it uses `is_scope_reachable` for scope-level reachability checking. This doesn't properly account for the actual text range of class definitions, causing incorrect filtering of type hierarchy results when scopes contain unreachable code.

## Requirements

1. The `is_scope_reachable` method should be removed from `semantic_index.rs`. The method currently performs recursive scope-level reachability checks and should be eliminated entirely.

2. The `reachability` field should be removed from the `Scope` struct in `scope.rs`. This field stores reachability constraints during scope construction and is no longer needed.

3. The `is_range_reachable` method in `semantic_index.rs` should be updated to determine scope reachability by walking ancestor scopes and examining their use-def maps directly. The implementation should use the `ancestor_scopes` iterator to traverse parent scopes.

4. The IDE type hierarchy code in `ide_support.rs` should use `is_range_reachable` instead of `is_scope_reachable` for checking reachability of class definitions. The reachability check should be based on the actual text range of class definitions being processed.

5. After these changes, the `ty_python_semantic` crate should compile cleanly with no warnings. All existing type checker behavior should be preserved — reachability checks for diagnostics and IDE features should continue to work correctly. The code should pass `cargo check`, `cargo clippy`, `cargo test`, and `cargo fmt` checks.
