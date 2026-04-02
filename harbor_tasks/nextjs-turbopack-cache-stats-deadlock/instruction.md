# Deadlock in turbo-tasks-backend `print_cache_item_size` instrumentation

## Bug Report

When the `print_cache_item_size` Cargo feature is enabled on the `turbo-tasks-backend` crate, the compilation process hangs indefinitely during `persist_snapshot`.

## Symptoms

- The build appears to hang forever with no error output
- Only happens when `print_cache_item_size` feature is enabled
- Thread dump shows a deadlocked thread waiting on an `RwLock`

## Root Cause (High Level)

During `persist_snapshot`, the storage iterates over all modified tasks. For each task, a read lock is acquired on a DashMap shard to get the `TaskStorage` reference. Then, inside a closure that still holds that read lock, a method is called to retrieve the task name for stats grouping. That method internally tries to acquire a **write lock** on the same DashMap shard (through `access_mut`). Since `parking_lot::RwLock` is not reentrant, the thread deadlocks waiting for its own read lock to be released.

## Relevant Code

- **File**: `turbopack/crates/turbo-tasks-backend/src/backend/mod.rs`
  - Look at the `persist_snapshot` method and the `process` closure
  - The stats-collection code inside `#[cfg(feature = "print_cache_item_size")]` blocks
  - The call that retrieves the task name for the stats hash map entry

- **File**: `turbopack/crates/turbo-tasks-backend/Cargo.toml`
  - The `print_cache_item_size` feature definition and its dependencies

## Additional Issues

1. The `print_cache_item_size` feature currently requires the `lzzzz` (lz4 compression) dependency even when you only want uncompressed size reporting. The compressed-size reporting should be opt-in behind a separate feature.

2. The stats output code has significant duplication — the same formatting pattern is repeated multiple times for different size fields, and the task name computation is duplicated.

## Expected Behavior

- Enabling `print_cache_item_size` should not cause a deadlock
- Uncompressed size reporting should work without pulling in the lz4 dependency
- The stats formatting code should be DRY

## Environment

- Crate: `turbo-tasks-backend` (inside the `turbopack/` subtree)
- Workspace: `turbopack/Cargo.toml`
