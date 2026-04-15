# turbo-persistence: is_empty() lock contention on hot read path

## Problem

The `is_empty()` method on `TurboPersistence` is called frequently on the hot read path (`lookup_task_candidates`) as a fast early-return before performing any real work. However, it currently acquires a read lock on the `RwLock<Inner>` just to check whether `meta_files` is empty — a boolean state that changes infrequently (only during `load_directory` and `commit`).

Taking a lock on every lookup, even a read lock, adds unnecessary contention and overhead. Under high concurrency, this becomes a bottleneck since every reader must coordinate through the `RwLock`.

## Expected Behavior

`is_empty()` must be lock-free. The required implementation:

1. Add a new `AtomicBool` field to the `TurboPersistence` struct that mirrors whether `meta_files` is empty. The struct already has an `active_write_operation: AtomicBool` field — a separate, additional `AtomicBool` field is needed for the emptiness state.
2. Rewrite `is_empty()` to use atomic `.load()` with `Ordering::Relaxed` instead of `self.inner.read()`.
3. Keep the `AtomicBool` in sync by calling `.store(meta_files.is_empty(), Ordering::Relaxed)` at every location where `meta_files` is modified (there are at least two such sites in the file, in different functions).

## Files to Look At

- `turbopack/crates/turbo-persistence/src/db.rs` — contains the `TurboPersistence` struct, `is_empty()` method, `load_directory()`, and `commit()` logic
