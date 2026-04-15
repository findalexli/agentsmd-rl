# Fix `uv export` extra resolution for workspace members with conflicting extras

## Problem

When running `uv export` on a workspace that has conflicting extras (e.g., `cpu` vs `cu124` for PyTorch), the exported requirements contain incorrect or missing marker expressions for workspace member dependencies.

The root cause spans two files:

1. In `crates/uv-resolver/src/universal_marker.rs`, the `resolve_conflicts` function only handles conflict-encoded extras (like `extra == 'extra-3-pkg-foo'`), but not unencoded/raw extras (like `extra == 'cpu'`). When a workspace member's dependency has a raw extra marker, the function incorrectly assumes it's always false because it has no way to interpret the extra name relative to a specific package.

2. In `crates/uv-resolver/src/lock/export/mod.rs`, the export graph doesn't track which extras each edge activates on its target dependency. Instead, extras are tracked per-node via a separate `selected_extras` HashMap, which doesn't correctly propagate through the dependency graph. The `Edge` enum uses tuple variants that only carry a marker tree, without any information about which dependency extras are activated.

## Expected Behavior

`uv export --extra cpu` for a workspace with conflicting `cpu`/`cu124` extras should produce correct marker expressions that properly reflect which packages are included under each extra.

### universal_marker.rs — scope-aware extra resolution

The extra/conflict resolution function should be named `resolve_activated_extras` (or kept as `resolve_conflicts`). It must accept a scope/package parameter (e.g., named `scope_package`, `package_name`, or similar) of type `Option<&PackageName>` representing the current package context.

When resolving an unencoded extra like `extra == 'cpu'`, the function should look it up as a `ConflictItem` composed of the scope package name and the extra name in the `known_conflicts` map. This allows raw extra markers to be correctly resolved against known activation conditions. The function body should contain logic that uses the scope parameter to construct a `ConflictItem` from the package name and raw extra name (e.g., via `package.clone()` and `name.clone()`).

### export/mod.rs — per-edge extras on Edge variants

The `Edge` enum must be converted from tuple variants to struct variants, with each variant including a field for the extras activated on the target dependency. The field should be named `dep_extras` (or `extras`, `child_extras`, or `activated_extras`) and hold a `Vec` of extra names.

### export/mod.rs — propagating extras in conflict_marker_reachability

The `conflict_marker_reachability` function must propagate the per-edge extras into the conflict map. When traversing an edge, it should:

- Extract the scope package from the parent graph node (e.g., via `package.name()`, `parent.name()`, or a `scope_package` variable derived from the node)
- Insert `ConflictItem`s for each extra carried by the edge into the parent's conflict map
- Pass the scope package and updated conflict map to the resolution function (`resolve_activated_extras` or `resolve_conflicts`)

## Files to Look At

- `crates/uv-resolver/src/universal_marker.rs` — contains the extra/conflict resolution function that needs a scope package parameter and logic for unencoded extra lookup
- `crates/uv-resolver/src/lock/export/mod.rs` — contains the `Edge` enum that needs dependency extras fields, and `conflict_marker_reachability` that needs to propagate them
