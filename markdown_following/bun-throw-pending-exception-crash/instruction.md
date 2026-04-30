# Bug: Bun crashes with assertion failure when a pending termination exception meets a new error

## Summary

When JavaScript code catches a stack overflow error and then triggers any operation that internally throws a new JS exception (e.g., a failing `expect()` matcher), Bun crashes with a `releaseAssertNoException` assertion failure instead of producing a normal JavaScript error.

## Symptom

When a termination exception (such as a stack overflow) is already pending on the JavaScriptCore VM, certain operations that internally call into the VM's error-throwing path cause the process to crash. The crash message mentions `releaseAssertNoException`.

The current code in some error-throwing functions uses `bun.assert(instance != .zero)` to assert that error creation succeeded. When a termination exception is pending, `createErrorInstance` returns `.zero` (indicating the exception was not created because one is already pending), and this assert fires — crashing the process instead of propagating the error.

## Reproduction

The following JavaScript reliably triggers the crash on the affected version of Bun:

```js
var a = false, b = false;
function r() { r() }
try { r() } catch(e) { a = true }
try { Bun.jest().expect(42).toBeFalse() } catch(e) { b = true }
if (a && b) console.log("OK")
```

A stack overflow is triggered via infinite recursion and caught. Then `Bun.jest().expect().toBeFalse()` is called, which internally creates and throws a new JS error. Because the VM still has the stack-overflow termination exception pending, the error-throwing path crashes with `releaseAssertNoException` instead of producing a catchable JavaScript error. On a correct fix, the script prints `OK` and exits with code 0.

## What to Look For

The relevant code lives in `src/bun.js/bindings/JSGlobalObject.zig`. Several error-throwing functions in this file are affected: `throw`, `throwPretty`, `throwValue`, `throwTODO`, `throwError` (the overload taking `anyerror`), and `createRangeError`. When any of these is called while a termination exception is already pending, they reach `VM.throwError` without first checking whether an exception is pending, which triggers the `releaseAssertNoException` crash inside JavaScriptCore.

Unrelated functions like `throwTypeError` and `throwDOMException` should continue to work as before and must not be stubbed or removed.

## Code Style Requirements

The repository enforces these conventions (documented in `src/CLAUDE.md`):

- Always use `bun.*` APIs rather than `std.*` equivalents. Use `bun.assert` instead of `std.debug.assert`. Avoid `std.fs`, `std.posix`, and `std.os`.
- Do not use `@import` inline inside function bodies.
- Do not use the deprecated `usingnamespace` keyword.
- Error handling paths must not use `@panic` or `unreachable` — use `error.JSError` for error returns.
- Do not use `std.debug.print` or `std.log` (debugging code must not be committed).
- Use spaces (not tabs) for indentation. The file must be valid UTF-8 with LF line endings.

## Acceptance Criteria

- The modified file must compile without errors (verified by `zig build-obj`).
- The `releaseAssertNoException` crash must no longer occur when an error is thrown while a termination exception is pending.
- The file must remain tracked in git and pass basic validation (`git diff --check`, `git cat-file`, `git check-attr`).
