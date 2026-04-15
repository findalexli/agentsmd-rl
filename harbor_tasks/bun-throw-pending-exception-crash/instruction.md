# Bug: Bun crashes with assertion failure after catching a stack overflow

## Summary

When JavaScript code catches a stack overflow error and then triggers any operation that internally throws a new JS exception (e.g., a failing `expect()` matcher), Bun crashes with a `releaseAssertNoException` assertion failure instead of producing a normal JavaScript error.

Crash fingerprint: `e9adb7008f7e2bd5`

## Reproduction

```javascript
var a = false, b = false;
function r() { r() }
try { r() } catch(e) { a = true }
try { Bun.jest().expect(42).toBeFalse() } catch(e) { b = true }
if (a && b) console.log("OK")
```

Expected: prints "OK" and exits cleanly.
Actual: process crashes with an assertion failure.

## Root Cause

The crash originates in `src/bun.js/bindings/JSGlobalObject.zig`. When a termination exception (such as a stack overflow) is pending on the JavaScriptCore VM, `createErrorInstance` returns `.zero`. Several functions in `JSGlobalObject` that call `createErrorInstance` do not handle this case — they either assert the return is non-zero or proceed to call into the VM's error-throwing path, which internally asserts no exception is already pending.

## Required Changes

Fix the following functions in `src/bun.js/bindings/JSGlobalObject.zig`:

1. **`throw`** - Must check if `createErrorInstance` returns `.zero` and return `error.JSError` instead of asserting non-zero with `bun.assert(instance != .zero)`.

2. **`throwPretty`** - Same pattern: must check if `createErrorInstance` returns `.zero` and return `error.JSError` instead of asserting non-zero.

3. **`throwTODO`** - Must check if `createErrorInstance` returns `.zero` and return `error.JSError` instead of proceeding to use the `.zero` value.

4. **`createRangeError`** - Must check if `createErrorInstance` returns `.zero` and handle it appropriately by returning `.zero` (after asserting `this.hasException()` is true).

5. **`throw`** with error options (the overload that takes a `comptime message, args` pattern for creating custom errors with `.code`, `.name`, `.errno` fields) - Must check if `createErrorInstance` returns `.zero` and return `error.JSError`.

6. **`throwValue`** - Must check `this.hasException()` (or equivalent) before calling `this.vm().throwError()`. When an exception is already pending, it should return `error.JSError` immediately instead of attempting to throw another error.

7. **`throwError(anyerror)`** - Must route through `throwValue` or have its own exception guard before calling `vm().throwError()`.

The pattern to use when checking for pending exceptions is:
- Check if `createErrorInstance` returned `.zero` OR check `this.hasException()` before throwing
- Assert that `this.hasException()` is true when `.zero` is returned
- Return `error.JSError` to propagate the error to callers

Do not use `@panic`, `unreachable`, or other crash-inducing constructs in error paths.
