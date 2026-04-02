# Bug: Panic when passing extreme float values as file descriptors

## Summary

Passing a very large floating-point number (e.g., `1e308` or `-1.5e308`) as a file descriptor to any API that internally uses `FD.fromJSValidated` causes the Bun runtime to panic with:

```
panic(main thread): integer part of floating point value out of bounds
```

This affects APIs like `Bun.S3Client.write` and any other function that accepts a numeric file descriptor argument.

## Reproduction

```js
// Any of these will crash bun instead of throwing a RangeError:
Bun.S3Client.write(1e308, "data");
Bun.S3Client.write(-1.5e308, "data");
Bun.S3Client.write(Infinity, "data");
Bun.S3Client.write(-Infinity, "data");
```

## Root Cause

The issue is in `src/fd.zig`, in the `fromJSValidated` function on the `FD` struct. The function receives a JavaScript number as a float, checks if it's an integer using `@mod(float, 1) != 0`, and then converts it to an `i64` before doing a range check.

The problem is that very large finite floats like `1e308` are technically integers in IEEE 754 (all doubles above 2^52 are whole numbers), so they pass the `@mod` check. But the subsequent conversion to `i64` panics because the value far exceeds the `i64` range.

## Expected Behavior

These calls should throw a `RangeError` (as they do for values like `-1` or `3000000000`), not crash the process.

## Files of Interest

- `src/fd.zig` — the `fromJSValidated` method on the `FD` struct
