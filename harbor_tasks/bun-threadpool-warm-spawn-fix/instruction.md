# ThreadPool.warm() Never Spawns Threads

There's a bug in the thread pool pre-warming logic that causes `warm(count)` to spawn far fewer threads than requested.

## The Symptom

The bundler calls `warm(8)` at startup to pre-create worker threads. Due to this bug, only a fraction of the requested threads are actually spawned upfront. The remaining threads get created lazily on demand, which defeats the purpose of pre-warming and hurts performance (especially on low-core machines where the worker pool is already small).

The bug manifests in at least three ways:
- **Loop condition**: The loop computes `to_spawn = count - sync.spawned` inside the loop body and uses it as the condition target, but `to_spawn` shrinks as spawned count grows — so the loop terminates early.
- **CAS result handling**: The code uses `cmpxchgWeak(...) orelse break` which breaks on success (null result), preventing any thread from being spawned when the CAS succeeds.
- **Early return**: `if (sync.spawned >= count) return;` causes warm() to exit prematurely if any threads were previously spawned, defeating pre-warming.
- **Stack size**: Both `warm()` and `notifySlow()` use a hardcoded `default_thread_stack_size` instead of the ThreadPool's configured `self.stack_size`.
- **Sync update placement**: The sync variable is updated inside the CAS assignment before thread.detach() is called, so it advances even when no thread was actually spawned.

## Where to Look

The relevant code is in `src/threading/ThreadPool.zig` in the `warm()` function and `notifySlow()` function.

Key observations:
- The function uses `cmpxchgWeak` for atomic compare-and-swap operations
- `cmpxchgWeak` returns null on success and non-null on failure (the old value)
- The logic involves a loop with a `while` condition
- There's a relationship between `count` (requested threads), `sync.spawned` (currently spawned), and `max_threads` (upper limit)
- Both `warm()` and `notifySlow()` configure thread spawn with `std.Thread.SpawnConfig`

## What Should Happen

When `warm(8)` is called on an empty pool with `max_threads >= 8`, all 8 threads should be spawned before the function returns. The `notifySlow()` function should also correctly spawn threads when needed.

After the fix, the following must be true of `warm()` in `ThreadPool.zig`:
1. The loop condition must use a stable target computed once before the loop, not a recalculated value.
2. `cmpxchgWeak` failure (non-null result) must be handled by retrying (continue), not by breaking.
3. There must be no early return that exits when `sync.spawned >= count`.
4. Both `warm()` and `notifySlow()` must use `self.stack_size` in their `SpawnConfig`, not `default_thread_stack_size`.
5. `sync` must be updated to `new_sync` after `thread.detach()` (not inside the CAS assignment).

After fixing the bug:
- All Zig source files in `src/threading/` (ThreadPool.zig, Mutex.zig, Condition.zig, Futex.zig, channel.zig, WaitGroup.zig, unbounded_queue.zig) must pass `zig fmt --check` and `zig ast-check`
- `src/bun.zig` and `src/cli.zig` must pass `zig ast-check`

Do NOT modify any test files. Your task is to fix the bug in the implementation.