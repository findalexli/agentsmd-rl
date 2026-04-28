# Bug: `mock.module()` crashes when first argument is not a string

## Summary

Calling `mock.module()` with a non-string first argument causes Bun's test runner to crash with an address-related error (`Address:unknown-crash:bun-debug+0x90074c1`) instead of throwing a clean `TypeError`.

## Reproduction

```ts
import { mock } from "bun:test";

// Any of these crash the process instead of throwing:
mock.module(SharedArrayBuffer, () => ({}));
mock.module({}, () => ({}));
mock.module(123, () => ({}));
mock.module(Symbol("test"), () => ({}));
```

Running any of the above in a test file with `bun test` causes a hard crash.

## Expected Behavior

`mock.module()` should throw a `TypeError` with the message `"mock(module, fn) requires a module name string"` when the first argument is not a string, similar to how other Bun APIs validate their arguments.

## Requirements

The fix must ensure that:
1. Passing a non-string value as the first argument to `mock.module()` throws a `TypeError` instead of crashing.
2. The error message is exactly `"mock(module, fn) requires a module name string"`.
3. The existing `argumentCount()` and `isEmpty()` validation guards remain in place.

## Test Requirements

Create a test file in `test/js/bun/` that:
- Verifies `mock.module()` throws `TypeError` for non-string arguments including `SharedArrayBuffer`, objects, numbers, and Symbols
- Asserts the error message contains `"mock(module, fn) requires a module name string"`
- Uses `toThrow` or similar assertions to verify the error is thrown
- Does not use `setTimeout`, custom timeouts, or shell commands like `find`/`grep`

## Code Style Requirements

- **TypeScript typechecking**: The repository uses `tsc --noEmit` for type checking. All code must pass typechecking.
- **JS linting**: The repository uses `oxlint` on `src/js/bun/` for JavaScript/TypeScript linting.
- **Banned words**: The repository has a banned words check (`test/internal/ban-words.test.ts`) that must pass.
- **Package.json lint**: The repository validates `package.json` files for exact version strings (`test/package-json-lint.test.ts`).
