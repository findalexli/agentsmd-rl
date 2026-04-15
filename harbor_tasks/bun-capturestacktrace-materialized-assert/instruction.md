# Bug: `Error.captureStackTrace` produces incorrect stack traces

## Summary

When `Error.captureStackTrace(err)` is called on an error object whose `.stack` property has already been accessed, the resulting `err.stack` may be empty, missing, or reflect the wrong capture point. In debug builds of the JavaScript engine, this can also cause an assertion failure during garbage collection.

## Reproduction

```js
function foo() {
  const err = new Error("test");
  // Force materialization by reading .stack
  const s = err.stack;
  // Now call captureStackTrace
  Error.captureStackTrace(err);
  return err.stack; // may be empty or stale
}

foo();
```

## Expected Behavior

`Error.captureStackTrace(err)` must produce a correct `.stack` value regardless of whether `err.stack` was previously accessed. The stack trace must reflect the location where `captureStackTrace` was called, not a previously materialized or empty value.

## Implementation Requirements

The fix is in `src/bun.js/bindings/FormatStackTraceForJS.cpp`, in the `errorConstructorFuncCaptureStackTrace` function. The following patterns must be present:

### Branching structure
- The function must use a **positive** `hasMaterializedErrorInfo()` conditional (an `if` with a corresponding `else` branch) to distinguish already-materialized errors from non-materialized ones.

### Materialized path (inside `if hasMaterializedErrorInfo()`)
- Must call `computeErrorInfoToJSValue` to compute the error info
- Must call `putDirect` to eagerly set the `.stack` property
- Must NOT call `setStackFrames` (that belongs in the non-materialized path)

### Non-materialized path (inside `else`)
- Must call `setStackFrames` to install the new stack frames
- Must call `deleteProperty` to remove the existing `.stack` property before installing a custom accessor
- Must call `putDirectCustomAccessor` to install a lazy accessor for `.stack`
- Must preserve `RETURN_IF_EXCEPTION` for exception safety

### General requirements
- Function must have at least 35 non-blank, non-comment lines
- Must use at least 4 distinct JSC API calls
- Code must use spaces for indentation (no tabs)
- File must include `#include "root.h"`
- File must end with a newline and have no trailing whitespace

## Affected Component

The `errorConstructorFuncCaptureStackTrace` host function in the JavaScriptCore bindings for Bun.
