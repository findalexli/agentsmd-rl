# Bug: Bun crashes with assertion failure when a pending termination exception meets a new error

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

When a termination exception (such as a stack overflow) is already pending on the JavaScriptCore VM, certain operations that internally call into the VM's error-throwing path will hit a `releaseAssertNoException` assertion because the VM detects that an exception is already pending.

The problem occurs in functions that call `createErrorInstance` — when it returns `.zero` (indicating an exception is already pending), the code must not proceed with the normal error-throwing machinery. Instead, it must detect this condition and return an error cleanly via Zig's error return type (`error.JSError`), without triggering assertions or crash-inducing constructs.

## What to Fix

The following functions all call `createErrorInstance` and must handle the case where it returns `.zero`:
- `throw()` and `throwPretty()` — currently use `bun.assert(instance != .zero)` which crashes; replace with `if (instance == .zero) { bun.assert(this.hasException()); return error.JSError; }`
- `throwTODO()` and `createRangeError()` — must add the same `.zero` handling pattern
- `throwValue()` — must guard against calling `vm().throwError()` when an exception is already pending; add `if (this.hasException()) return error.JSError;` before `vm().throwError`
- `throwError(anyerror)` — must route through `throwValue` (which has the guard) rather than calling `vm().throwError` directly

Error handling must use `error.JSError` for propagated errors. Do not use `@panic`, `unreachable`, or other crash-inducing constructs in error paths.

## File Location

The code to modify lives in the Zig bindings for Bun's JavaScript runtime, in a file that defines `pub const JSGlobalObject = opaque` near the top and contains the throw functions listed above. The file is tracked in the Bun repository under `src/`.