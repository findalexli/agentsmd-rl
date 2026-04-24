# Optimize get_compilation_issues MCP tool to use whole-app module graph

## Problem

The `get_compilation_issues` MCP tool in this Next.js repository is extremely slow on large applications. The async function responsible for collecting all compilation issues (in the `next-napi-bindings` crate) iterates over every endpoint group and computes separate per-route module graphs. This means the work scales as O(routes) graph computations when a single whole-app module graph computation would suffice.

A method for computing whole-app module graphs already exists on the `Project` type (in the `next-api` crate) — it calls `drop_issues()` in development mode to suppress compilation issues and prevent duplicate per-route HMR noise. This makes it unsuitable for the MCP tool, which needs to collect ALL issues.

## Expected Behavior

### 1. New whole-app graph method on Project (without issue suppression)

Add a new method to `impl Project` that computes the whole-app module graph **without** suppressing issues. This method must:
- Be annotated with `#[turbo_tasks::function]`
- Use the existing `whole_app_module_graph_operation` for graph computation
- Call `.connect()` on the result to ensure proper task graph connection
- NOT call `drop_issues` — it must preserve all compilation issues
- Have "whole_app" in its name, distinct from the existing `whole_app_module_graphs`

### 2. Compilation issues function must use whole-app graph

The function that collects all compilation issues must use a whole-app graph method instead of iterating endpoint groups:
- It must call a `.whole_app_module_graph` method
- It must NOT call `get_all_endpoint_groups`
- It must NOT contain the pattern `endpoint_group` followed by `module_graphs`

### 3. Extract scale-down logic to a free helper function

The node pool scale-down logic currently inlined in `whole_app_module_graphs` (involving `node_backend`, `scale_down`, `scale_zero`, and `execution_context`) must be extracted into a separate **free async function** — not inside any `impl` block. This free function should handle both `scale_down` and `scale_zero` operations. After extraction, `whole_app_module_graphs` should call this helper instead of inlining the logic.

### 4. Preserve the original `whole_app_module_graphs` method

The existing `whole_app_module_graphs` method on `Project` must remain functional and unchanged in its behavior — it still needs to drop issues in dev mode for HMR subscriptions. It must continue to:
- Be annotated with `#[turbo_tasks::function]`
- Contain `drop_issues` and `is_production` logic

## Relevant Code

The changes span two crates, each containing a file named `project.rs`:
- The `next-api` crate — contains the `Project` type, `whole_app_module_graphs`, and the `whole_app_module_graph_operation` function
- The `next-napi-bindings` crate (under `src/next_api/`) — contains the compilation issues collection function

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`
