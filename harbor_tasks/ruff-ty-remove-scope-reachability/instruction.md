# Remove per-scope reachability tracking from ty semantic index

## Problem

The ty type checker's semantic index tracks reachability at the scope level via a dedicated `reachability` field on each `Scope` and a recursive `is_scope_reachable` method on `SemanticIndex`. This per-scope tracking is redundant — the more general `is_range_reachable` method (which checks statement-level reachability via use-def maps) can be extended to walk ancestor scopes, making the scope-level reachability field and method unnecessary dead code.

The `Scope` struct in `scope.rs` carries a `reachability` field of type `ScopedReachabilityConstraintId` that is stored, propagated during scope construction, and consulted — but its functionality overlaps entirely with `is_range_reachable`.

## Expected Behavior

After removing the dead code, the crate should compile cleanly with no warnings. All existing type checker behavior should be preserved — `is_range_reachable` should iterate up through ancestor scopes using their use-def maps instead of delegating to a separate `is_scope_reachable` call.

## Files to Look At

- `crates/ty_python_semantic/src/semantic_index.rs` — contains the `is_scope_reachable` method to remove and `is_range_reachable` method to simplify
- `crates/ty_python_semantic/src/semantic_index/scope.rs` — contains the `Scope` struct with the `reachability` field to remove
- `crates/ty_python_semantic/src/semantic_index/builder.rs` — contains scope construction logic that passes `reachability` to `push_scope_with_parent`
- `crates/ty_python_semantic/src/types/ide_support.rs` — contains a call to `is_scope_reachable` that needs to be replaced with `is_range_reachable`
