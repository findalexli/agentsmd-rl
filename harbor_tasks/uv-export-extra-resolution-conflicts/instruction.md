# Fix `uv export` extra resolution for workspace members with conflicting extras

## Problem

When running `uv export` on a workspace that has conflicting extras (e.g., `cpu` vs `cu124` for PyTorch), the exported requirements contain incorrect or missing marker expressions for workspace member dependencies.

The root cause is that the export graph builder resolves extra markers too early. Specifically:

1. The `resolve_conflicts` function in `universal_marker.rs` only handles conflict-encoded extras (like `extra == 'extra-3-pkg-foo'`), but not unencoded/raw extras (like `extra == 'cpu'`). When a workspace member's dependency has a raw extra marker, the function incorrectly assumes it's always false.

2. The export graph doesn't track which extras each edge activates on its target dependency. Instead, extras are tracked per-node via a separate `selected_extras` HashMap, which doesn't correctly propagate through the dependency graph.

## Expected Behavior

`uv export --extra cpu` for a workspace with conflicting `cpu`/`cu124` extras should produce correct marker expressions that properly reflect which packages are included under each extra.

The extra resolution must happen in the context of the current package scope, and each graph edge must carry information about which extras it activates on the target dependency.

## Files to Look At

- `crates/uv-resolver/src/universal_marker.rs` — contains the `resolve_conflicts` function that resolves extra markers against known conflict items. It needs to handle unencoded extras by looking them up relative to the current package scope.
- `crates/uv-resolver/src/lock/export/mod.rs` — builds the export dependency graph. The `Edge` enum and `conflict_marker_reachability` function need to propagate per-edge extras through the graph.
