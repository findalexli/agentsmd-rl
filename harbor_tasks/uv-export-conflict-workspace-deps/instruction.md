# Bug: `uv export --package` produces empty output for conflicting workspace members

## Summary

When a workspace has two members declared as conflicting via `[tool.uv].conflicts` (package-level conflicts), running `uv export --package <member>` produces empty output — the member's dependencies are missing from the exported requirements file.

## Reproduction

1. Create a workspace with two child members (`child-a`, `child-b`), each depending on a different version of the same package (e.g., `sortedcontainers==2.3.0` vs `sortedcontainers==2.4.0`).
2. Declare them as package-level conflicts in the root `pyproject.toml`:
   ```toml
   [tool.uv]
   conflicts = [
     [
       { package = "child-a" },
       { package = "child-b" },
     ],
   ]
   ```
3. Run `uv lock` (succeeds).
4. Run `uv export --package child-a` — the output is empty (no dependencies listed).
5. Run `uv export --package child-b` — also empty.

A non-conflicting workspace member in the same workspace exports correctly.

The same bug affects `--format pylock.toml` exports.

## Relevant Code

The export logic lives in `crates/uv-resolver/src/lock/export/mod.rs`, specifically in the `ExportableRequirements::from_lock` method. This method builds a dependency graph for export by:

1. Adding workspace root packages to the graph
2. Tracking which packages/extras are "activated" in the conflict set
3. Queuing their dependencies for traversal
4. Resolving conflicts via marker trees during traversal

The bug is in how activated packages are tracked in the conflict set during the graph-building phase. When a workspace member is added to the export graph under the production dependencies path, its activation is not properly registered in the conflicts map. This causes the downstream conflict resolution to incorrectly exclude the member's dependencies.

## Expected Behavior

`uv export --package child-a` should include `child-a` and its dependency `sortedcontainers==2.3.0` in the output, just like a non-conflicting member would.
