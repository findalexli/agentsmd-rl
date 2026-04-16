# Bug: Crash when accessing `server.url` with invalid unix socket path

## Summary

When using `Bun.serve()` with a `unix` option that results in an unparseable URL (e.g., passing a non-string value), accessing `server.url` causes a hard crash (segfault) instead of throwing a proper JavaScript error.

## Reproduction

```js
const server = Bun.serve({
  unix: Bun, // non-string value — gets stringified to "[object Bun]"
  fetch() {
    return new Response("ok");
  },
});
server.url; // crashes the process instead of throwing a JavaScript error
```

## Expected Behavior

Accessing `server.url` when the URL is invalid should throw a proper JavaScript error (e.g., a JavaScript exception that can be caught with try/catch), not crash the entire process with a segmentation fault.

## Requirements

When the fix is applied:
1. Accessing `server.url` with an invalid URL must throw a JavaScript exception instead of crashing
2. The fix must be a pure insertion — no existing lines may be modified or removed
3. The fix must be applied to the C++ binding function that converts BunString to a JS URL object. The function has a throw scope and performs a C-style cast after creating the JS object. A guard is needed to return early if an exception is pending, preventing the cast from executing on an invalid value.