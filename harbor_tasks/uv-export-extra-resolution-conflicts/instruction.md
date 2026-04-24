# Fix `uv export` extra resolution for workspace members with conflicting extras

## Problem

When running `uv export` on a workspace that has conflicting extras (e.g., `cpu` vs `cu124` for PyTorch), the exported requirements contain incorrect or missing marker expressions for workspace member dependencies.

The root cause spans two files:

1. In `crates/uv-resolver/src/universal_marker.rs`, the extra/conflict resolution function only handles conflict-encoded extras (like `extra == 'extra-3-pkg-foo'`), but not unencoded/raw extras (like `extra == 'cpu'`). When a workspace member's dependency has a raw extra marker, the function incorrectly assumes it's always false because it has no way to interpret the extra name relative to a specific package.

2. In `crates/uv-resolver/src/lock/export/mod.rs`, the export graph doesn't track which extras each edge activates on its target dependency. Instead, extras are tracked per-node via a separate `selected_extras` HashMap, which doesn't correctly propagate through the dependency graph. The `Edge` enum uses tuple variants that only carry a marker tree, without any information about which dependency extras are activated.

## Expected Behavior

`uv export --extra cpu` for a workspace with conflicting `cpu`/`cu124` extras should produce correct marker expressions that properly reflect which packages are included under each extra.

### universal_marker.rs — scope-aware extra resolution

The extra/conflict resolution function must accept a scope/package parameter representing the current package context (e.g., an `Option<&PackageName>` parameter named something like `scope_package`, `package_name`, `scope`, `pkg_name`, or `current_package`).

When resolving an unencoded extra like `extra == 'cpu'`, the function must look it up as a `ConflictItem` composed of the scope package name and the extra name in the `known_conflicts` map. This allows raw extra markers to be correctly resolved against known activation conditions.

The implementation should contain logic that uses the scope parameter to construct a `ConflictItem` from the package name and raw extra name.

### export/mod.rs — per-edge extras on Edge variants

The `Edge` enum must include, on each variant, a field for the extras activated on the target dependency. The field should be named something like `dep_extras`, `extras`, `child_extras`, or `activated_extras` and hold a collection of extra names.

### export/mod.rs — propagating extras in conflict_marker_reachability

The `conflict_marker_reachability` function must propagate the per-edge extras into the conflict map. When traversing an edge, it should:

- Extract the scope package from the parent graph node
- Insert `ConflictItem`s for each extra carried by the edge into the parent's conflict map
- Pass the scope package and updated conflict map to the resolution function

## Files to Look At

- `crates/uv-resolver/src/universal_marker.rs` — contains the extra/conflict resolution function that needs a scope package parameter and logic for unencoded extra lookup
- `crates/uv-resolver/src/lock/export/mod.rs` — contains the `Edge` enum that needs dependency extras fields, and `conflict_marker_reachability` that needs to propagate them

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`
