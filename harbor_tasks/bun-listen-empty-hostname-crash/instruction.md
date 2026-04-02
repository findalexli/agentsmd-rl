# Bug: `Bun.listen()` and `Bun.connect()` crash on truthy values that coerce to empty string

## Summary

`Bun.listen()` and `Bun.connect()` crash with an internal assertion failure when the `hostname` (or `unix`) option is a truthy value whose `toString()` returns an empty string. For example, passing an empty array `[]` or `new String("")` as the hostname causes a panic instead of a proper error.

## Reproduction

```js
Bun.listen({
  hostname: [],
  port: 0,
  socket: { data() {}, open() {}, close() {} }
});
// Expected: TypeError — "Expected a non-empty "hostname""
// Actual: Internal assertion failure — panic/crash
```

The same crash occurs with `Bun.connect()` using the same kind of inputs.

## Root Cause

The socket option parsing code in `src/bun.js/api/bun/socket/Handlers.zig` (inside `SocketConfig.fromJS`) uses the bindgen `IDLLooseNullable` conversion for the `hostname` and `unix` options. This conversion checks the truthiness of the original JS value (objects like `[]` are truthy), then calls `toString()` to get the string value. When `toString()` produces `""`, the result is a non-null string with length zero. The Zig code then hits an assertion that assumes a truthy bindgen string can never be empty — but it can, because truthiness was checked on the original JS object, not on the coerced string.

## Expected Fix

Replace the assertions with proper validation that returns a descriptive `TypeError` when the coerced string is empty, rather than panicking. This follows the existing error-handling pattern already used elsewhere in the same function (e.g., the port validation a few lines below).

## Files to Investigate

- `src/bun.js/api/bun/socket/Handlers.zig` — the `SocketConfig.fromJS` function, specifically the `unix` and `hostname` option handling branches

## Testing

Add tests to `test/js/bun/net/socket.test.ts` that verify both `Bun.listen()` and `Bun.connect()` properly throw (not crash) when given truthy values that coerce to empty strings for hostname/unix options.
