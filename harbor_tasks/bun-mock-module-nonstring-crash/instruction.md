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

## Expected Behavior

`mock.module()` should throw a `TypeError` with a clear message when the first argument is not a string, similar to how other Bun APIs validate their arguments.

## Requirements

1. **Type validation must occur before string conversion**: The implementation must check that the first argument is a string before attempting any string conversion operations. Acceptable type guard patterns include: `isString(`, `isCell(`, `isObject(`, `isSymbol(`, `isNumber(`, `isUndefinedOrNull(`, `isBoolean(`, `isHeapBigInt(`, `jsTypeInfo(`, `JSType::` string checks, `toStringOrNull`, or `tryGetString`.

2. **Error must be thrown with early return**: When the first argument fails type validation, the code must throw an exception (using patterns like `throwException`, `createTypeError`, `createError`, `throwTypeError`, or `ThrowTypeError`) and return early (using `return;`, `return JSValue`, `return js`, or `RETURN_IF_EXCEPTION`).

3. **Error message must be descriptive**: The error message should mention "string", "module", or "specifier" so the user understands what went wrong.

4. **Existing validation must be preserved**: The current `argumentCount()` and `isEmpty()` validation guards must remain in place.
