# Bug: `mock.module()` crashes when first argument is not a string

## Summary

Calling `mock.module()` with a non-string first argument (e.g., `SharedArrayBuffer`, an object, a number, or a Symbol) causes Bun's test runner to crash with an address-related error instead of throwing a clean `TypeError`.

## Reproduction

```ts
import { mock } from "bun:test";

// Any of these crash the process instead of throwing:
mock.module(SharedArrayBuffer, () => ({}));
mock.module({}, () => ({}));
mock.module(123, () => ({}));
mock.module(Symbol("test"), () => ({}));
```

Running any of the above in a test file with `bun test` causes a hard crash. The crash fingerprint is: `Address:unknown-crash:bun-debug+0x90074c1`.

## Root Cause

The `JSMock__jsModuleMock` function in `src/bun.js/bindings/BunPlugin.cpp` calls `.toString()` on the first argument before validating that it is actually a string. When a non-string value like `SharedArrayBuffer` is passed, `toString()` produces something like `"function SharedArrayBuffer() { [native code] }"`, which the module resolver then tries to auto-install as a package. This triggers a crash because the package manager's logger allocator is uninitialized in this context.

## Expected Behavior

`mock.module()` should throw a `TypeError` with a clear message when the first argument is not a string, similar to how other Bun APIs like `Jest.call()` validate their arguments.

## Relevant Files

- `src/bun.js/bindings/BunPlugin.cpp` — the `JSMock__jsModuleMock` function (around line 500)
