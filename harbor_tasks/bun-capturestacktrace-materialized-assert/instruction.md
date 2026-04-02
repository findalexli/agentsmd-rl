# Bug: `Error.captureStackTrace` crashes when error info is already materialized

## Summary

Calling `Error.captureStackTrace(err)` on an error object whose `.stack` property has already been accessed causes a crash during garbage collection. The crash manifests as an assertion failure: `ASSERT(!m_errorInfoMaterialized)` inside `computeErrorInfo` when GC's `finalizeUnconditionally` encounters unmarked stack frames.

## Reproduction

```js
function foo() {
  const err = new Error("test");
  // Force materialization by reading .stack
  const s = err.stack;
  // Now replace frames — this triggers the crash
  Error.captureStackTrace(err);
  return err.stack;
}

foo();
// In a debug build: assertion failure in finalizeUnconditionally
// In a release build: use-after-free / intermittent crash under GC pressure
```

The crash is more likely to trigger under GC pressure (e.g., in a loop or with `gc()` calls), because the dangling `m_stackTrace` pointer from `setStackFrames` is only problematic once GC tries to finalize the error instance.

## Affected file

`src/bun.js/bindings/FormatStackTraceForJS.cpp` — the `errorConstructorFuncCaptureStackTrace` function.

## Root cause

When `.stack` is first accessed on an `ErrorInstance`, JSC materializes the error info (computes the stack string from frames, sets `m_errorInfoMaterialized = true`, and clears `m_stackTrace`). The current `captureStackTrace` implementation unconditionally calls `setStackFrames()` after materialization, which sets a new `m_stackTrace` while `m_errorInfoMaterialized` remains `true`. JSC's `computeErrorInfo` has an assertion that `m_stackTrace` is null when `m_errorInfoMaterialized` is true — this invariant is violated, causing the assertion failure.

The key constraint is that JSC's `ErrorInstance` enforces an invariant: when `m_errorInfoMaterialized` is true, `m_stackTrace` must be null. The current code violates this by calling `setStackFrames()` unconditionally after `materializeErrorInfoIfNeeded()`.

## Expected behavior

`Error.captureStackTrace(err)` should work correctly regardless of whether `err.stack` was previously accessed. The resulting `.stack` property should reflect the new capture point, and no assertion failures or crashes should occur during garbage collection.
