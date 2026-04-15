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
server.url; // crashes the process
```

## Expected Behavior

Accessing `server.url` when the URL is invalid should throw a proper JavaScript error, not crash the process. The crash occurs in `src/bun.js/bindings/BunString.cpp` in the `BunString__toJSDOMURL` function: when `DOMURL::create()` fails to parse a string and returns an exception, the code proceeds to dereference a null pointer. Adding a guard that returns early on exception before the dereference prevents the crash.
