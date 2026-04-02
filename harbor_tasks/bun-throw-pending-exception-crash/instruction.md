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

## Relevant Code

The crash originates in `src/bun.js/bindings/JSGlobalObject.zig`, in the error-throwing machinery. When a termination exception (such as a stack overflow) is pending on the JavaScriptCore VM, `createErrorInstance` returns `.zero`. Several functions in `JSGlobalObject` that call `createErrorInstance` do not handle this case — they either assert the return is non-zero or proceed to call into the VM's error-throwing path, which internally asserts no exception is already pending.

Look at how `throw`, `throwPretty`, and related error-throwing functions handle the return value of `createErrorInstance`, and how `throwValue` interacts with the VM when an exception is already active.
