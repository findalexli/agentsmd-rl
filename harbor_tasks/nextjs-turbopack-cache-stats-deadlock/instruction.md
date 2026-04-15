# Deadlock in turbo-tasks-backend `print_cache_item_size` Instrumentation

## Bug Report

When the `print_cache_item_size` Cargo feature is enabled on the `turbo-tasks-backend` crate, the compilation process hangs indefinitely during `persist_snapshot`.

## Symptoms

- The build appears to hang forever with no error output
- Only happens when `print_cache_item_size` feature is enabled
- Thread dump shows a deadlocked thread waiting on an `RwLock`

## Root Cause (High Level)

During `persist_snapshot`, the storage iterates over all modified tasks. For each task, a read lock is acquired on a DashMap shard to get the `TaskStorage` reference. Then, inside a closure that still holds that read lock, a method is called to retrieve the task name for stats grouping. That method internally tries to acquire a **write lock** on the same DashMap shard (through `access_mut`). Since `parking_lot::RwLock` is not reentrant, the thread deadlocks waiting for its own read lock to be released.

## Expected Behavior

- Enabling `print_cache_item_size` should not cause a deadlock
- Uncompressed size reporting should work without pulling in the lz4 dependency (`lzzzz`)
- The stats formatting code should be DRY (no repetition of formatting patterns)

## Required Changes

### 1. Fix the Deadlock

The stats code in `persist_snapshot` calls `.entry(self.get_task_name(...))` which acquires a write lock while a read lock is already held. To retrieve the task name without re-locking, the task name must be derived from the **already-locked `TaskStorage` reference** (`inner`). The correct approach reads from this reference directly — do not call a method that re-acquires the lock.

The fix must:
- Replace all `.entry(self.get_task_name(task_id, turbo_tasks))` calls inside `#[cfg(feature = "print_cache_item_size")]` blocks with entries derived from the storage reference directly
- Not use `self.` in any `.entry()` argument inside the stats cfg block

### 2. Split the Cargo Feature

The `print_cache_item_size` feature currently requires the `lzzzz` (lz4 compression) dependency even when you only want uncompressed size reporting. You must:

- Make `print_cache_item_size` a standalone feature with no `lzzzz` dependency
- Add a separate feature (e.g., `print_cache_item_size_with_compressed`) that extends `print_cache_item_size` and adds `lzzzz`

### 3. Fix the `add_counts` Guard

The stats collection calls `.add_counts()` on a task only when `encode_meta` is true. However, tasks that only have data modifications (no meta changes) are missed. Change the guard to `encode_data || encode_meta` so all modified tasks are counted.

### 4. Introduce a Formatting Struct

The repeated formatting pattern for size fields should be refactored into a helper struct with a `Display` implementation. This struct should format raw sizes and, when a compressed-size feature is enabled, also show compressed sizes.

## Relevant Files

- **Source**: `turbopack/crates/turbo-tasks-backend/src/backend/mod.rs`
  - Look at the `persist_snapshot` method and the `process` closure
  - The stats-collection code inside `#[cfg(feature = "print_cache_item_size")]` blocks
  - The `TaskCacheStats` struct and its impl block

- **Cargo**: `turbopack/crates/turbo-tasks-backend/Cargo.toml`
  - The `[features]` section defines the feature flags

## Environment

- Crate: `turbo-tasks-backend` (inside the `turbopack/` subtree)
- Workspace: `turbopack/Cargo.toml`

## Notes

- No Rust toolchain is available in the Docker image. Tests use Python subprocess scripts that parse the Rust source for required patterns.
- Stats infrastructure must still exist after the fix (not just deleted to avoid the bug)
- The `print_cache_item_size_with_compressed` feature, when enabled, gates the compressed-size fields and lz4 dependency