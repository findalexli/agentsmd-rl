# Fix AbortSignal leak in ReadableStream.pipeTo with signal option

## Problem

When `ReadableStream.prototype.pipeTo` is called with a `signal` option and the pipe never completes (e.g., the readable stream never enqueues data), the `AbortSignal` is **never garbage collected**. This causes a 100% memory leak - each call leaks one AbortSignal.

### The cycle

```
AbortSignal (RefCounted)
  -> m_algorithms[i] (lambda capturing Ref<JSAbortAlgorithm>)
  -> JSCallbackDataStrong::m_callback (JSC::Strong = GC root)
  -> callback closure
  -> pipeState.signal (JSAbortSignal wrapper)
  -> Ref<AbortSignal>  <- cycle
```

`JSAbortAlgorithm` currently holds its JS callback via `JSCallbackDataStrong`, which creates a `JSC::Strong` handle (a GC root). The abort algorithm closure registered by `pipeTo` captures `pipeState`, which holds `pipeState.signal` (the `JSAbortSignal` wrapper). Since the wrapper holds a `Ref<AbortSignal>`, the cycle is complete and nothing can be collected.

## Expected Behavior

When all JavaScript references to an AbortSignal are dropped and the pipe never completes, the AbortSignal should be garbage collected. No Strong reference cycle should prevent collection.

## Files to Look At

- `src/bun.js/bindings/webcore/JSAbortAlgorithm.h` — The JS callback wrapper class
- `src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp` — Implementation of handleEvent
- `src/bun.js/bindings/webcore/AbortSignal.h` — The signal class with algorithm storage (see `m_algorithms` member)
- `src/bun.js/bindings/webcore/AbortSignal.cpp` — add/remove/run abort algorithms
- `src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp` — GC visitation hook

## Reference Patterns

Look at these existing patterns in the Bun codebase for guidance on breaking GC cycles:

1. **Weak callback patterns** — See `JSPerformanceObserverCallback` (`src/bun.js/bindings/webcore/JSPerformanceObserverCallback.{h,cpp}`)

2. **Thread-safe vector + lock patterns** — See `EventListenerMap::visitJSEventListeners` (`src/bun.js/bindings/webcore/EventListenerMap.h:77-85`)

## Context

This is a memory leak in the Web Streams API implementation. The leak occurs because `pipeTo` stores an abort algorithm that keeps the signal alive indefinitely when the pipe never completes.

The fix must break the `JSCallbackDataStrong` reference cycle while keeping the JS callback alive during GC. The `JSAbortAlgorithm` class needs to use a weak reference pattern that allows GC collection when the signal wrapper is unreachable, while ensuring the callback is marked when the signal is reachable.
