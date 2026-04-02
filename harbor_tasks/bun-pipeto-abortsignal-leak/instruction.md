# AbortSignal memory leak in ReadableStream.pipeTo

## Bug Description

When `ReadableStream.prototype.pipeTo` is called with a `signal` option and the pipe never completes (e.g., the readable stream never closes or errors), dropping all JavaScript-side references to the `AbortController` and its signal does **not** allow the `AbortSignal` to be garbage collected. This results in a 100% memory leak of every `AbortSignal` passed to `pipeTo`.

## Reproduction

Running 200 iterations of creating a `ReadableStream` that never resolves its `pull()`, piping it to a `WritableStream` with a signal, and then letting all references go out of scope results in ~201 retained `AbortSignal` objects (verified via `bun:jsc` `heapStats()`). After GC, the count should drop to near zero, but it doesn't.

## Root Cause

There is a reference cycle in the C++ binding layer:

1. `AbortSignal` (ref-counted) holds abort algorithm callbacks
2. The abort algorithm registered by `pipeTo` captures the pipe state, which holds a reference back to the `JSAbortSignal` wrapper
3. The `JSAbortAlgorithm` class holds its JS callback via a mechanism that creates a GC root, preventing the garbage collector from ever breaking the cycle

## Relevant Files

- `src/bun.js/bindings/webcore/AbortSignal.cpp` / `AbortSignal.h` — the C++ `AbortSignal` class that stores abort algorithms
- `src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp` / `JSAbortAlgorithm.h` — the JS-to-C++ callback wrapper for abort algorithms
- `src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp` — custom GC visiting logic for `JSAbortSignal`

## Hints

- Look at how `JSAbortAlgorithm` stores its callback reference and whether it creates a strong GC root
- Consider how other callback wrappers in the codebase (e.g., `JSPerformanceObserverCallback`) avoid similar cycles by using weak references with GC visitor support
- The fix needs to ensure abort algorithms still fire correctly when `abort()` is called, while allowing GC to collect unreachable signals
- Thread safety matters: the GC visitor runs on a separate thread, so any shared data structures need proper synchronization
