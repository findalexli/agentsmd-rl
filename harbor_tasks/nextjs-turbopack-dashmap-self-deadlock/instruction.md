# Fix DashMap read-write self-deadlock in task_cache

## Problem

The Turbopack backend hangs during incremental builds with persistent caching. After several incremental rebuilds, all tokio worker threads end up blocked on `dashmap::lock::RawRwLock::lock_exclusive_slow`, causing a complete system freeze.

The hang originates in the task cache lookup path. When looking up an existing task in `task_cache` (a `DashMap<Arc<CachedTaskType>, TaskId>`), the code acquires a read lock on a shard via `task_cache.get()`. The returned `dashmap::Ref` holds that read lock. Before the `Ref` is dropped, the code calls into `ConnectChildOperation::run`, which can trigger an aggregation update that calls `task_cache.entry().or_insert()` — requiring a write lock. When this targets the same shard, the thread self-deadlocks because DashMap's `RawRwLock` is not reentrant.

## Expected Behavior

The read lock on `task_cache` should be released before any code path that might need a write lock on the same map. Incremental builds with persistent caching should not hang regardless of how many rebuild cycles occur.

## Files to Look At

- `turbopack/crates/turbo-tasks-backend/src/backend/mod.rs` — Contains `get_or_create_persistent_task` and `get_or_create_transient_task`, both of which perform the `task_cache` lookup followed by `ConnectChildOperation::run`. Both functions have the same deadlock pattern.
