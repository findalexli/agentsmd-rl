# ThreadPool.warm() Never Spawns Threads

There's a bug in the thread pool pre-warming logic that causes `warm(count)` to spawn far fewer threads than requested.

## The Symptom

The bundler calls `warm(8)` at startup to pre-create worker threads. Due to this bug, only a fraction of the requested threads are actually spawned upfront. The remaining threads get created lazily on demand, which defeats the purpose of pre-warming and hurts performance (especially on low-core machines where the worker pool is already small).

## Where to Look

The relevant code is in `src/threading/ThreadPool.zig` in the `warm()` function.

Key observations:
- The function uses `cmpxchgWeak` for atomic compare-and-swap operations
- The logic involves incrementing `sync.spawned` and spawning threads in a loop
- There's a relationship between `count` (requested threads), `sync.spawned` (currently spawned), and `max_threads` (upper limit)

## What Should Happen

When `warm(8)` is called on an empty pool with `max_threads >= 8`, all 8 threads should be spawned before the function returns.

## Hints

- Look at how the loop termination condition is computed
- Check what happens when `cmpxchgWeak` succeeds vs fails
- The variable used to track how many threads to spawn may be computed incorrectly
- Consider: what should happen on CAS success? What should happen on CAS failure?

## Files to Modify

- `src/threading/ThreadPool.zig` - specifically the `warm()` function and possibly `notifySlow()`

Do NOT modify any test files. Your task is to fix the bug in the implementation.
