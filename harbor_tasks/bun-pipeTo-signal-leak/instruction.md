# Fix AbortSignal leak in ReadableStream.pipeTo with signal option

## Problem

When `ReadableStream.prototype.pipeTo` is called with a `signal` option and the pipe never completes (e.g., the readable stream never enqueues data), the `AbortSignal` is **never garbage collected**. This causes a 100% memory leak - each call leaks one AbortSignal.

### The cycle

```
AbortSignal (RefCounted)
  → m_algorithms[i] (lambda capturing Ref<JSAbortAlgorithm>)
  → JSCallbackDataStrong::m_callback (JSC::Strong = GC root)
  → callback closure
  → pipeState.signal (JSAbortSignal wrapper)
  → Ref<AbortSignal>  ← cycle
```

`JSAbortAlgorithm` held its JS callback via `JSCallbackDataStrong`, which creates a `JSC::Strong` handle (a GC root). The abort algorithm closure registered by `pipeTo` captures `pipeState`, which holds `pipeState.signal` (the `JSAbortSignal` wrapper). Since the wrapper holds a `Ref<AbortSignal>`, the cycle is complete and nothing can be collected.

## Expected Behavior

When all JavaScript references to an AbortSignal are dropped and the pipe never completes, the AbortSignal should be garbage collected. No Strong reference cycle should prevent collection.

## Files to Look At

- `src/bun.js/bindings/webcore/JSAbortAlgorithm.h` — The JS callback wrapper class
- `src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp` — Implementation of handleEvent
- `src/bun.js/bindings/webcore/AbortSignal.h` — The signal class with algorithm storage
- `src/bun.js/bindings/webcore/AbortSignal.cpp` — add/remove/run abort algorithms
- `src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp` — GC visitation hook

## The Fix Pattern

The fix follows two existing patterns in the Bun codebase:

1. **JSCallbackDataWeak + visitJSFunction override** — Same as `JSPerformanceObserverCallback` (`src/bun.js/bindings/webcore/JSPerformanceObserverCallback.{h,cpp}`)

2. **Lock + Vector + GC-thread visit** — Same as `EventListenerMap::visitJSEventListeners` (`src/bun.js/bindings/webcore/EventListenerMap.h:77-85`)

Key changes needed:
1. Switch `JSAbortAlgorithm` from `JSCallbackDataStrong` to `JSCallbackDataWeak`
2. Add `visitJSFunction` methods to `JSAbortAlgorithm` for GC marking
3. Add a separate `m_abortAlgorithms` vector in `AbortSignal` (kept separate from `m_algorithms` so GC can visit weak callbacks)
4. Add `visitAbortAlgorithms` method to `AbortSignal` for GC visitation
5. Call `visitAbortAlgorithms` from `JSAbortSignal::visitAdditionalChildrenInGCThread`
6. Handle null callback in `handleEvent` (Weak ref can be collected)
7. Update `memoryCost()` to include the new vector

## References

- Look at how `JSPerformanceObserverCallback` implements weak callbacks
- Look at `EventListenerMap` for the lock + vector + GC-thread pattern
- The PR description has detailed cycle analysis and fix explanation
