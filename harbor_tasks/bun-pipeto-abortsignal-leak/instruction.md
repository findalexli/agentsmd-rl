# AbortSignal Memory Leak in ReadableStream.pipeTo

## Bug Description

When `ReadableStream.prototype.pipeTo` is called with a `signal` option and the pipe never completes (e.g., the readable stream never closes or errors), dropping all JavaScript-side references to the `AbortController` and its signal does **not** allow the `AbortSignal` to be garbage collected. This results in a 100% memory leak of every `AbortSignal` passed to `pipeTo`.

Running 200 iterations of creating a `ReadableStream` that never resolves its `pull()`, piping it to a `WritableStream` with a signal, and then letting all references go out of scope results in ~201 retained `AbortSignal` objects (verified via `bun:jsc` `heapStats()`). After GC, the count should drop to near zero, but it doesn't.

## Files to Modify

The implementation lives in these files in the Bun repository at `/workspace/bun`:

- `src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp`
- `src/bun.js/bindings/webcore/JSAbortAlgorithm.h`
- `src/bun.js/bindings/webcore/AbortSignal.cpp`
- `src/bun.js/bindings/webcore/AbortSignal.h`
- `src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp`

You must also create:

- `test/js/web/streams/pipeTo-signal-leak.test.ts`

## Acceptance Criteria

The fix must satisfy all of the following:

1. **No strong reference cycle**: After dropping all JS references to a signal used in a `pipeTo` that never completes, GC must be able to collect the `AbortSignal` and its associated `AbortAlgorithm` objects.

2. **Abort must still work**: Calling `controller.abort()` on a signal used with `pipeTo` must still correctly abort the pipe and clean up all resources.

3. **Thread-safe algorithm storage**: Abort algorithms must be stored in a container that is safe to access from multiple threads, with proper locking around mutations.

4. **GC-visitor integration**: The GC must be able to trace through all abort algorithms to keep alive any JS function references that are still reachable.

5. **Memory accounting accuracy**: The `memoryCost()` method must account for all algorithm storage.

6. **No setTimeout in regression test**: The regression test file must not use `setTimeout`; use `Bun.sleep()` instead.

7. **Module-scope imports in regression test**: All imports in the regression test must be at module scope, not inside test function bodies via dynamic `import()`.

## Regression Test Requirements

Create `test/js/web/streams/pipeTo-signal-leak.test.ts` that:

- Uses `bun:jsc` `heapStats()` to measure `AbortSignal` retention
- Tests that dropping signal references allows GC collection when pipe never completes
- Tests that aborting a signal still works and cleans up properly
- Does NOT use `setTimeout` (use `Bun.sleep()` instead)
- Uses only module-scope static imports (no dynamic `import()` calls inside test bodies)

## Code Quality Requirements

The following code quality checks will be performed:

- **Shell scripts**: The repo scripts `scripts/check-node.sh`, `scripts/check-node-all.sh`, and `scripts/run-clang-format.sh` (if present) must pass shellcheck validation with severity set to error.
- **C++ syntax validation**: All modified C++ files must have balanced `{`/`}` braces and balanced `(`/`)` parentheses, with valid `#include` directives (using `<...>` or `"..."` syntax).
- **Code style**: Each target file may have at most 5 lines containing tab characters.
- **Header structure**: Header files must use either `#pragma once` or traditional include guards (`#ifndef`/`#define`/`#endif`).

## Required Patterns in C++ Code

The C++ implementation must include the following patterns (the tests verify their presence):

### Weak Callback Mechanism
The `JSAbortAlgorithm` class must use a weak callback mechanism instead of a strong one. Tests check that:
- No `JSCallbackDataStrong` type appears in the implementation
- A weak callback type (such as `JSCallbackDataWeak` or equivalent) is used in member/constructor context

### GC Visitor Method
`JSAbortAlgorithm` must have a visitor method that allows the GC to trace through its callback reference.

### Null Guard in handleEvent
The `handleEvent` method must guard against the case where the callback has been garbage collected (null check before use).

### Typed Algorithm Container
`AbortSignal` must store abort algorithms in a typed container separate from any type-erased lambda storage, with a visitor method for GC tracing.

### Thread Safety
The algorithm storage must use proper locking. Tests verify:
- A lock/mutex member variable exists
- At least two lock usages appear in the implementation

### GC Visitor Walks Algorithms
The `JSAbortSignalCustom` GC visitor must iterate or call through to the abort algorithm visitor so callbacks remain reachable during GC.

### Memory Cost Accounting
The `memoryCost()` method must include accounting for the new abort algorithms container.

### Separate Storage Path
Algorithms must be stored via a method that appends to the new container, NOT via the old type-erased `addAlgorithm` path. Similarly, removal must operate on the new container with proper locking.