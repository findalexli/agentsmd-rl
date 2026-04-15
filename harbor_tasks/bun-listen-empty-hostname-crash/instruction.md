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
// Expected: TypeError
// Actual: Internal assertion failure — panic/crash
```

The same crash occurs with `Bun.connect()` using the same kind of inputs.

## Root Cause

The socket option parsing code uses a bindgen conversion that checks the truthiness of the original JS value (objects like `[]` are truthy), then calls `toString()` to get the string value. When `toString()` produces `""`, the result is a non-null string with length zero. The code then hits an `assertf` crash assertion that assumes a truthy bindgen string can never be empty — but it can, because truthiness was checked on the original JS object, not on the coerced string.

## Expected Fix

Replace the crash assertions with proper validation that returns a descriptive `TypeError` when the coerced string is empty. Use one of these error-throwing patterns already established in the Bun codebase:
- `throwInvalidArguments`
- `throwTypeError`
- `throwPossiblyInvalidArguments`

Or manually check: when `length == 0`, return an error.

This follows the existing error-handling pattern already used elsewhere in the socket configuration handling (e.g., the port validation a few lines below in the same function).

## Files to Investigate

- Look for socket-related files in `src/bun.js/api/bun/socket/` — specifically where socket configuration options like `hostname` and `unix` are parsed from JavaScript

## Testing

Add tests to `test/js/bun/net/socket.test.ts` that verify both `Bun.listen()` and `Bun.connect()` properly throw (not crash) when given truthy values that coerce to empty strings for hostname/unix options.

The tests must:
- Include assertions for throwing behavior (using `toThrow`, `throw`, or `reject`)
- Test the bug trigger patterns: `[]` (empty array), `String("")`, or empty values combined with hostname/unix options
- Cover both `Bun.listen()` and `Bun.connect()` APIs
