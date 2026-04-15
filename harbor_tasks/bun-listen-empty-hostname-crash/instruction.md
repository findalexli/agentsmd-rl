# Bug: `Bun.listen()` and `Bun.connect()` crash on truthy values that coerce to empty string

## Symptom

`Bun.listen()` and `Bun.connect()` panic/crash with an internal assertion failure when the `hostname` (or `unix`) option is a truthy value whose `toString()` returns an empty string. For example, passing an empty array `[]` or `new String("")` as the hostname causes a crash instead of a proper error.

```js
Bun.listen({
  hostname: [],
  port: 0,
  socket: { data() {}, open() {}, close() {} }
});
// Expected: TypeError
// Actual: crash
```

## Task

Fix `src/bun.js/api/bun/socket/Handlers.zig` so that `Bun.listen()` and `Bun.connect()` return a descriptive error (not crash) when given truthy-but-empty values for hostname or unix options.

Add tests to `test/js/bun/net/socket.test.ts` that verify the fix works. The test file must:
- Have more than 500 lines total (do not truncate existing tests)
- Contain test blocks using `it()` or `test()` with a description
- Test both `Bun.listen()` and `Bun.connect()` APIs
- Use trigger patterns: empty array `[]` with hostname, or `String("")` style values
- Assert throwing behavior using `toThrow`, `throw`, or `reject`

The source file `src/bun.js/api/bun/socket/Handlers.zig` must:
- Have at least 200 lines (do not delete or gut existing code)
- Keep the existing hostname and unix handling branches intact
- Replace the crash assertion with proper error handling

## What "proper error handling" means

The error should be a descriptive TypeError. When the fix is correct, code like this:

```js
Bun.listen({ hostname: [], port: 0, socket: { data() {}, open() {}, close() {} } });
```

...will throw an exception that can be caught, rather than crashing the process.

## Files

- `src/bun.js/api/bun/socket/Handlers.zig` — contains the socket configuration parsing code
- `test/js/bun/net/socket.test.ts` — the existing test file (add your new tests here, keep existing tests intact)