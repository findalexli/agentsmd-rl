# ThreadPool Pre-warming Issue

The bundler's thread pool pre-warming mechanism is not working correctly. When `warm()` is called to pre-create worker threads, fewer threads than requested are actually spawned upfront. The remaining threads get created lazily on demand instead, defeating the purpose of pre-warming and hurting performance.

## Expected Behavior

When `warm(count)` is called on a thread pool that has fewer than `count` threads already spawned, the pool should spawn enough threads to reach `count` total spawned threads (respecting `max_threads` as an upper bound). All threads should be created before the function returns.

## Verification

After your fix, all Zig source files in `src/threading/` (ThreadPool.zig, Mutex.zig, Condition.zig, Futex.zig, channel.zig, WaitGroup.zig, unbounded_queue.zig) must pass `zig fmt --check` and `zig ast-check`.

Additionally, `src/bun.zig` and `src/cli.zig` must pass `zig ast-check`.

## Task

Fix the bug in the thread pool pre-warming logic so that calling `warm(count)` actually spawns `count` threads (or up to `max_threads`) before returning. Currently, fewer threads are spawned than requested.

Do NOT modify any test files. Your task is to fix the bug in the implementation.