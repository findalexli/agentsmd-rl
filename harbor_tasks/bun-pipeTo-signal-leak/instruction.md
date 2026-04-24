# AbortSignal Memory Leak in ReadableStream.pipeTo

## Symptom

When `ReadableStream.prototype.pipeTo` is called with an `AbortSignal` option and the pipe never completes (e.g., the readable stream never enqueues data), the `AbortSignal` is **never garbage collected**. Each such call leaks one AbortSignal, causing memory to grow unbounded.

## Root Cause

A reference cycle prevents garbage collection: the AbortSignal holds a strong reference to the JavaScript abort callback, which captures a reference back to the signal, forming a cycle that keeps both alive even when no external references remain.

## Correct Behavior

When all JavaScript references to an AbortSignal are dropped and the pipe never completes, the AbortSignal must be garbage collected.

## Implementation Requirements

The fix must satisfy all of the following constraints:

1. **Break the strong-reference cycle** — JavaScript abort callbacks must not hold strong references back to the signal. The implementation must use a weak callback data type (not a strong one) so the GC can collect the callback independently.

2. **Support GC traversal** — The GC must be able to traverse through the signal to find and mark any JavaScript callbacks attached to it. The implementation must provide a `visitJSFunction` method on abort algorithms and a `visitAbortAlgorithms` method on the signal that the GC visitor can call.

3. **Handle invalid callbacks gracefully** — When a callback has been garbage collected, the signal must not attempt to invoke it. The `handleEvent` implementation must null-check the callback before use.

4. **Use lock-protected storage** — The signal must store JavaScript abort algorithms in a collection protected by a lock. The storage must use `Vector<std::pair<uint32_t, Ref<AbortAlgorithm>>>` guarded by a `Lock` member, with `Locker` used around all accesses.

5. **Atomic algorithm extraction in runAbortSteps** — The `runAbortSteps` function must atomically extract all algorithms from storage (using `std::exchange` or similar) before iterating and invoking them.

6. **Account for all memory** — The `memoryCost` function must include the size of the JavaScript abort algorithm storage (`m_abortAlgorithms.sizeInBytes()`).

7. **Implement add/remove primitives** — The implementation must provide `addAbortAlgorithmToSignal` and `removeAbortAlgorithmFromSignal` functions that operate on the lock-protected storage with a `Locker` pattern and `append`/`removeFirstMatching` operations.

## Affected Files

The fix involves these files in the WebCore bindings directory:
- `src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp` and `JSAbortAlgorithm.h`
- `src/bun.js/bindings/webcore/AbortSignal.cpp` and `AbortSignal.h`
- `src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp`

## Verification

After the fix:
- The `JSAbortAlgorithm` class must use `JSCallbackDataWeak` (not `JSCallbackDataStrong`)
- The `JSAbortAlgorithm` class must declare `visitJSFunction` methods for GC marking
- The `AbortSignal` class must declare `visitAbortAlgorithms` template method
- `runAbortSteps` must use atomic extraction (`std::exchange` or `std::move`) before iteration
- `memoryCost` must call `sizeInBytes` on the abort algorithm storage
- No memory leak when `pipeTo` is called with an AbortSignal that never completes