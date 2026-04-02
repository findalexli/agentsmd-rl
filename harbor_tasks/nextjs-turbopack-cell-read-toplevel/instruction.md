# Bug: Cell reads incorrectly forbidden in top-level tasks

## Summary

In the turbo-tasks runtime (`turbopack/crates/turbo-tasks/src/manager.rs`), the `try_read_task_cell` method incorrectly panics with a debug assertion when called from a top-level task. The assertion was originally intended to prevent **eventually consistent** reads (like task output reads) from top-level tasks, since those can return stale data. However, cell reads are **strongly consistent** — they always return up-to-date data — so there is no semantic reason to block them.

## Reproduction

The existing test file `turbopack/crates/turbo-tasks-backend/tests/top_level_task_consistency.rs` contains a test `test_cell_read_in_top_level_task_fails` that demonstrates the issue. In a `run_once` (top-level task) context, resolving a value via `resolve_strongly_consistent()` and then reading the resulting cell with `.await` causes a panic in debug builds, even though this operation should succeed.

The restriction should only apply to eventually consistent reads (task output reads via `.connect().await`), not to cell reads. The `try_read_task_output` and `try_read_local_output` methods correctly guard against top-level task usage, but `try_read_task_cell` should not have this restriction.

## Relevant files

- `turbopack/crates/turbo-tasks/src/manager.rs` — the `try_read_task_cell` method (around line 1470)
- `turbopack/crates/turbo-tasks-backend/tests/top_level_task_consistency.rs` — test that demonstrates the false-positive panic
