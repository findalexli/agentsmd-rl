# Optimize get_compilation_issues MCP tool to use whole-app module graph

## Problem

The `get_compilation_issues` MCP tool is extremely slow on large Next.js applications. The function `get_all_compilation_issues_inner_operation` in `crates/next-napi-bindings/src/next_api/project.rs` iterates over every endpoint group and computes separate per-route module graphs via `endpoint_group.module_graphs()`. This means the work scales as O(routes) graph computations when a single whole-app module graph computation would suffice.

The obvious optimization would be to use `Project::whole_app_module_graphs()`, but that method calls `drop_issues()` in development mode to prevent duplicate per-route HMR noise. This suppresses the exact issues the MCP tool needs to collect.

## Expected Behavior

The `get_all_compilation_issues_inner_operation` function should compute a single whole-app module graph instead of iterating endpoint groups, while still preserving the ability to collect compilation issues (i.e., not dropping them).

The existing `whole_app_module_graphs()` method must remain unchanged — it still needs to drop issues in dev mode for HMR subscriptions.

## Files to Look At

- `crates/next-api/src/project.rs` — Contains `Project::whole_app_module_graphs()` and the `whole_app_module_graph_operation` function. The node pool scale-down logic is currently inlined in `whole_app_module_graphs`.
- `crates/next-napi-bindings/src/next_api/project.rs` — Contains `get_all_compilation_issues_inner_operation` which currently does per-endpoint iteration.
