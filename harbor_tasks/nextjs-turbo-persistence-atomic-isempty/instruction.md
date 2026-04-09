# turbo-persistence: is_empty() lock contention on hot read path

## Problem

The `is_empty()` method on `TurboPersistence` is called frequently on the hot read path (`lookup_task_candidates`) as a fast early-return before performing any real work. However, it currently acquires a read lock on the `RwLock<Inner>` just to check whether `meta_files` is empty — a boolean state that changes very infrequently (only during `load_directory` and `commit`).

Taking a lock on every lookup, even a read lock, adds unnecessary contention and overhead. Under high concurrency, this becomes a bottleneck since every reader must coordinate through the `RwLock`.

## Expected Behavior

`is_empty()` should be lock-free. Since the emptiness state only changes at two well-defined mutation points, it can be tracked without acquiring the `RwLock` on every read.

## Files to Look At

- `turbopack/crates/turbo-persistence/src/db.rs` — contains the `TurboPersistence` struct, `is_empty()` method, `load_directory()`, and `commit()` logic
