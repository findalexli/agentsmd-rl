# AbortSignal memory leak in ReadableStream.pipeTo

## Bug Description

When `ReadableStream.prototype.pipeTo` is called with a `signal` option and the pipe never completes (e.g., the readable stream never closes or errors), dropping all JavaScript-side references to the `AbortController` and its signal does **not** allow the `AbortSignal` to be garbage collected. This results in a 100% memory leak of every `AbortSignal` passed to `pipeTo`.

Running 200 iterations of creating a `ReadableStream` that never resolves its `pull()`, piping it to a `WritableStream` with a signal, and then letting all references go out of scope results in ~201 retained `AbortSignal` objects (verified via `bun:jsc` `heapStats()`). After GC, the count should drop to near zero, but it doesn't.

## Files Related to This Issue

- `src/bun.js/bindings/webcore/AbortSignal.cpp` — implementation of the C++ `AbortSignal` class
- `src/bun.js/bindings/webcore/AbortSignal.h` — header for the C++ `AbortSignal` class
- `src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp` — implementation of the JS-to-C++ callback wrapper for abort algorithms
- `src/bun.js/bindings/webcore/JSAbortAlgorithm.h` — header for the JS-to-C++ callback wrapper
- `src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp` — custom GC visiting logic for `JSAbortSignal`
- `test/js/web/streams/pipeTo-signal-leak.test.ts` — regression test file (must be created)

## Test Validation Requirements

The following implementation patterns are validated by the test suite:

1. **Weak callback mechanism**: `JSAbortAlgorithm.cpp` and `JSAbortAlgorithm.h` must use a weak reference type (`JSCallbackDataWeak`, `WeakPtr`, `Weak<`, `weakCallback`, or `JSWeakValue`) and must NOT use `JSCallbackDataStrong`.

2. **GC visitor delegation**: `JSAbortAlgorithm` must implement a GC visitor method (matching pattern `(void|template).*visit|trace|mark.*(Visitor|Slot)`) that delegates to its callback data member.

3. **Null guard in handleEvent**: The `handleEvent` method in `JSAbortAlgorithm.cpp` must include a null/validity guard check (patterns like `!callback`, `callback == nullptr`, `!m_data`, or `callback.has_value`).

4. **Typed container for algorithms**: `AbortSignal.h` must declare a typed container for abort algorithms (using `Vector`, `HashMap`, `Deque`, `std::vector`, or similar with `AbortAlgorithm` or `Ref<AbortAlgorithm>`) separate from the existing `m_algorithms` field.

5. **Container visitor method**: `AbortSignal` must declare and implement a visitor method for the abort algorithm container (matching pattern `visit|trace|mark.*Abort|Algorithm|Callback`).

6. **Thread-safety**: `AbortSignal.h` must include a lock/mutex member (patterns like `Lock`, `Mutex`, `std::mutex`, `m_*Lock`, `m_*Mutex`, `WTF_GUARDED_BY_LOCK`, or `std::atomic`) and `AbortSignal.cpp` must show at least 2 lock usages (patterns like `Locker`, `lock_guard`, `unique_lock`, `scoped_lock`, `.lock()`, `LockHolder`, or `AutoLocker`).

7. **GC visitor integration**: `JSAbortSignalCustom.cpp` must implement a GC visitor method (matching `visitAdditionalChildren|visitChildren|visitOutputConstraints|trace.*Visitor|Slot`) that walks abort algorithms via the visitor method or iteration.

8. **addAbortAlgorithmToSignal storage**: The `addAbortAlgorithmToSignal` function in `AbortSignal.cpp` must NOT call `addAlgorithm()` and must use container insertion (patterns like `append`, `push_back`, `emplace_back`, `emplace`, or `insert`) with proper locking.

9. **removeAbortAlgorithmFromSignal cleanup**: The `removeAbortAlgorithmFromSignal` function in `AbortSignal.cpp` must NOT call `removeAlgorithm()` and must use container removal (patterns like `removeFirstMatching`, `remove_if`, `erase`, or `removeAll`) with proper locking.

10. **memoryCost accounting**: The `memoryCost` method in `AbortSignal.cpp` must account for the abort algorithms container size (patterns like `m_abort.*sizeInBytes`, `m_abort.*size`, `m_abort.*capacity`, or `m_abort.*byteSize`).

## Regression Test Requirements

Create `test/js/web/streams/pipeTo-signal-leak.test.ts` that:
- Uses `bun:jsc` `heapStats()` to measure `AbortSignal` retention
- Tests that dropping signal references allows GC collection when pipe never completes
- Tests that aborting a signal still works and cleans up properly
- Does NOT use `setTimeout` (use `Bun.sleep()` instead)
- Uses only module-scope static imports (no dynamic `import()` calls inside test bodies)
