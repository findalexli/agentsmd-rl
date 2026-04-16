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

- The function implementing `Error.captureStackTrace` must handle both materialized and non-materialized error states correctly.
- When error info has already been materialized, the implementation must not violate JSC's internal invariants (specifically, it must not cause `ASSERT(!m_errorInfoMaterialized)` failures).
- The function must have at least 35 non-blank, non-comment lines.
- Must use at least 4 distinct JSC API calls from this set: `jsDynamicCast`, `RETURN_IF_EXCEPTION`, `putDirect`, `deleteProperty`, `setStackFrames`, `hasMaterializedErrorInfo`, `materializeErrorInfoIfNeeded`, `computeErrorInfo`, `getFramesForCaller`, `DeletePropertyModeScope`, `putDirectCustomAccessor`.
- Code must use spaces for indentation (no tabs).
- File must include `#include "root.h"`.
- File must end with a newline and have no trailing whitespace.
