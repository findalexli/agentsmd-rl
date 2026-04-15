# ThreadPool.warm() Never Spawns Threads

There's a bug in the thread pool pre-warming logic that causes `warm(count)` to spawn far fewer threads than requested.

## The Symptom

The bundler calls `warm(8)` at startup to pre-create worker threads. Due to this bug, only a fraction of the requested threads are actually spawned upfront. The remaining threads get created lazily on demand, which defeats the purpose of pre-warming and hurts performance (especially on low-core machines where the worker pool is already small).

## Where to Look

The relevant code is in `src/threading/ThreadPool.zig` in the `warm()` function.

Key observations:
- The function uses `cmpxchgWeak` for atomic compare-and-swap operations
- The logic involves a loop with a `while (sync.spawned < ...)` condition
- There's a relationship between `count` (requested threads), `sync.spawned` (currently spawned), and `max_threads` (upper limit)

## Required Implementation Patterns

The fix must introduce the following specific code patterns:

1. A `target` variable computed as:
   ```zig
   const target = @min(count, @as(u14, @truncate(self.max_threads)));
   ```

2. A `while` loop that compares `sync.spawned` against `target`:
   ```zig
   while (sync.spawned < target) {
   ```

3. A `cmpxchgWeak` call that handles failure by capturing `|current|` and continuing:
   ```zig
   if (self.sync.cmpxchgWeak(...)) |current| {
       sync = @as(Sync, @bitCast(current));
       continue;
   }
   ```

4. `thread.spawn()` must use `self.stack_size` instead of `default_thread_stack_size` in both `warm()` and `notifySlow()`.

## What Should NOT Be Present

After the fix, the `warm()` function should no longer contain:
- The pattern `count - sync.spawned` for computing spawn count
- An early return like `if (sync.spawned >= count) return;`
- `cmpxchgWeak` followed by `orelse break` (this exits on success instead of failure)
- Usage of `default_thread_stack_size` in the spawn config

## What Should Happen

When `warm(8)` is called on an empty pool with `max_threads >= 8`, all 8 threads should be spawned before the function returns.

## Hints

- The current code uses a "delta" approach (spawning `count - already_spawned` threads) which is incorrect
- The fix should use a "target" approach (spawning threads until `sync.spawned` reaches a target value)
- On CAS success (cmpxchgWeak returns null), spawn the thread and update `sync` for the next iteration
- On CAS failure (cmpxchgWeak returns the current value), refresh `sync` and retry
- After `thread.detach()`, update `sync = new_sync` for correct state tracking in the next iteration

## Files to Modify

- `src/threading/ThreadPool.zig` - specifically the `warm()` function and `notifySlow()`

Do NOT modify any test files. Your task is to fix the bug in the implementation.
