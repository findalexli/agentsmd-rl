# Bug: Bun crashes with assertion failure when a pending termination exception meets a new error

## Summary

When JavaScript code catches a stack overflow error and then triggers any operation that internally throws a new JS exception (e.g., a failing `expect()` matcher), Bun crashes with a `releaseAssertNoException` assertion failure instead of producing a normal JavaScript error.

## Symptom

When a termination exception (such as a stack overflow) is already pending on the JavaScriptCore VM, certain operations that internally call into the VM's error-throwing path cause the process to crash. The crash message mentions `releaseAssertNoException`.

## What to Look For

The relevant code lives in `src/bun.js/bindings/JSGlobalObject.zig`. Error-throwing functions in that file may crash when called while a termination exception is already pending. The crash occurs because the VM's error-throwing path is invoked without checking whether an exception is already pending.