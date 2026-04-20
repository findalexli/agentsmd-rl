# AbortSignal Memory Leak in ReadableStream.pipeTo

## Symptom

When `ReadableStream.prototype.pipeTo` is called with an `AbortSignal` option and the pipe never completes (e.g., the readable stream never enqueues data), the `AbortSignal` is **never garbage collected**. Each such call leaks one AbortSignal, causing memory to grow unbounded.

## Root Cause

A Strong reference cycle prevents collection:
```
AbortSignal -> JSAbortAlgorithm -> Strong<callback> -> closure -> pipeState.signal -> JSAbortSignal -> Ref<AbortSignal>
```

The `JSAbortAlgorithm` class stores a `JSCallbackDataStrong*` (via `m_data`), which strongly holds the JavaScript callback. This callback captures references back to the signal, creating a cycle that prevents GC even when no external references to the signal remain.

## Expected Behavior

When all JavaScript references to an AbortSignal are dropped and the pipe never completes, the AbortSignal should be garbage collected. To break the cycle:

1. `JSAbortAlgorithm` must use **weak references** (`JSCallbackDataWeak`) instead of strong references (`JSCallbackDataStrong`)
2. The weak callback must be visited during GC so it doesn't get collected prematurely
3. `handleEvent` must check if the weak callback is still valid (non-null) before using it

## Implementation Requirements

Modify the following files in `/workspace/bun/src/bun.js/bindings/webcore/`:

### 1. JSAbortAlgorithm.h and JSAbortAlgorithm.cpp

**JSAbortAlgorithm.h changes:**
- Change `callbackData()` return type from `JSCallbackDataStrong*` to `JSCallbackDataWeak*`
- Change `m_data` member type from `JSCallbackDataStrong*` to `JSCallbackDataWeak*`
- Add two `visitJSFunction` override methods:
  - `void visitJSFunction(JSC::AbstractSlotVisitor&) override`
  - `void visitJSFunction(JSC::SlotVisitor&) override`

**JSAbortAlgorithm.cpp changes:**
- In the constructor, initialize `m_data` with `new JSCallbackDataWeak(vm, callback, this)` instead of `new JSCallbackDataStrong`
- In `handleEvent`, check if `callback` is null before using it. If null, return `CallbackResultType::UnableToExecute`
- Implement the two `visitJSFunction` methods to delegate to `m_data->visitJSFunction(visitor)`

### 2. AbortSignal.h

Add to the `AbortSignal` class:
- A new member `visitAbortAlgorithms` template method: `template<typename Visitor> void visitAbortAlgorithms(Visitor&)`
- A new storage member for JS abort algorithms: `Vector<std::pair<uint32_t, Ref<AbortAlgorithm>>> m_abortAlgorithms`
- A lock member for thread safety: `Lock m_abortAlgorithmsLock`
- Include `<wtf/Lock.h>` if not already present

### 3. AbortSignal.cpp

Modify the implementation:
- In `runAbortSteps`: Use `std::exchange` to atomically extract and process `m_abortAlgorithms`, calling `handleEvent` on each
- In `addAbortAlgorithmToSignal`: Use `m_abortAlgorithms.append()` with proper locking instead of `addAlgorithm()`
- In `removeAbortAlgorithmFromSignal`: Use `m_abortAlgorithms.removeFirstMatching()` with locking instead of `removeAlgorithm()`
- In `memoryCost`: Add `m_abortAlgorithms.sizeInBytes()` to the returned size
- Add explicit template instantiations for `visitAbortAlgorithms<JSC::AbstractSlotVisitor>` and `visitAbortAlgorithms<JSC::SlotVisitor>`

### 4. JSAbortSignalCustom.cpp

In `visitAdditionalChildrenInGCThread`, add a call to `wrapped().visitAbortAlgorithms(visitor)` to ensure the weak JS callbacks are visited during GC.

## Verification

After the fix:
- `JSCallbackDataWeak` should be instantiated exactly once (in JSAbortAlgorithm)
- `JSCallbackDataStrong` should not be used in JSAbortAlgorithm
- The `visitJSFunction` methods must have the `override` specifier
- `m_abortAlgorithms` must be protected by `m_abortAlgorithmsLock`
- `handleEvent` must null-check the callback before dereferencing
