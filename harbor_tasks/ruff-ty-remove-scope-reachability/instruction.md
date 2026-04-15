# Remove per-scope reachability tracking from ty semantic index

## Problem

The ty type checker's semantic index maintains redundant reachability tracking at the scope level. Each `Scope` carries a dedicated field for reachability constraints (`reachability`) that is stored during scope construction and propagated through various scope-related methods. A method called `is_scope_reachable` performs recursive scope-level reachability checks.

This per-scope tracking overlaps entirely with the more general range-based reachability checking provided by `is_range_reachable`. The `is_range_reachable` method currently delegates to `is_scope_reachable` before checking use-def maps, creating unnecessary complexity. Scope reachability could instead be determined by walking ancestor scopes and checking their use-def maps directly, eliminating the need for a separate scope-level tracking mechanism.

Additionally, the IDE support for type hierarchy has a reachability bug: when iterating over class definitions to build the subtype hierarchy, it calls `is_scope_reachable` which doesn't properly account for the actual code range of the class definition. This causes incorrect filtering of type hierarchy results when scopes contain unreachable code. The fix should use range-based reachability checking that considers the actual class definition's text range.

## Requirements

1. The `is_scope_reachable` method should be removed entirely - it is dead code that creates unnecessary recursive complexity.

2. The `reachability` field on the `Scope` struct should be removed, along with any constructor parameters related to it and any code that marks reachability constraints as used during scope finalization.

3. The `is_range_reachable` method should be updated to walk ancestor scopes directly using their use-def maps instead of delegating to `is_scope_reachable`. The `ancestor_scopes` iterator on `SemanticIndex` provides a way to iterate through parent scopes.

4. The IDE type hierarchy code that currently calls `is_scope_reachable` should be updated to use `is_range_reachable` with the proper text range of the class definition being checked.

5. After these changes, the crate should compile cleanly with no warnings. All existing type checker behavior should be preserved — reachability checks for diagnostics and IDE features should continue to work correctly.

## Files to Look At

- `crates/ty_python_semantic/src/semantic_index.rs` - contains `is_scope_reachable` and `is_range_reachable` methods
- `crates/ty_python_semantic/src/semantic_index/scope.rs` - contains the `Scope` struct with the `reachability` field
- `crates/ty_python_semantic/src/semantic_index/builder.rs` - contains scope construction logic with reachability parameters
- `crates/ty_python_semantic/src/types/ide_support.rs` - contains type hierarchy IDE support with the reachability bug
