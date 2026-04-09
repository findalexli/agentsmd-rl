# turbo-tasks-backend: stability fixes for task cancellation and error handling

## Problem

The `turbo-tasks-backend` has several interrelated stability issues that surface when filesystem caching is enabled:

1. **"Cell no longer exists" errors on incremental rebuilds after a task error.** When a task fails partway through execution, its `cell_type_max_index` is updated from incomplete `cell_counters`, which removes entries for cell types not yet encountered during the partial execution. Tasks that still hold dependencies on those cells then hit hard errors because the cell appears to no longer exist. This manifests specifically with `serialization = "hash"` cell types (e.g. `FileContent`), where cell data is transient and readers fall back to `cell_type_max_index` to decide whether to schedule recomputation.

2. **Shutdown hangs on `stop_and_wait`.** When a task is cancelled during shutdown, readers waiting on in-progress cells that will never be filled are never notified, so foreground jobs hang indefinitely.

3. **Cache poisoning from cancelled tasks.** When a task is cancelled, a `"was canceled"` error may be persisted as task output. Subsequent builds that read from the cache then hit stale errors and break until the cache is manually cleared.

## Expected Behavior

- When a task errors, `cell_type_max_index` should be preserved as-is (not updated from partial counters), consistent with how cell data is already preserved on error.
- When a task is cancelled, all pending in-progress cell events should be drained and notified so waiters can proceed.
- Cancelled tasks should be marked dirty for the next session so stale error outputs are invalidated, preventing cache poisoning.
- When reading a cell from a cancelled task, the code should bail early before registering a listener that would never resolve.

## Files to Look At

- `turbopack/crates/turbo-tasks-backend/src/backend/mod.rs` — The main backend implementation containing `try_read_task_cell`, `task_execution_canceled`, and `task_execution_completed_prepare`
- `turbopack/crates/turbo-tasks-backend/src/backend/operation/mod.rs` — The `TaskGuard` trait and dirty state management utilities
