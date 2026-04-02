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

The URL formatter produces a string like `unix://[object Bun]` which is not a valid WHATWG URL. The internal C++ function that converts a `BunString` to a `DOMURL` object does not handle the case where URL parsing fails — when `DOMURL::create()` returns an exception, the code proceeds to dereference a null pointer.

## Relevant Code

The crash occurs in `src/bun.js/bindings/BunString.cpp` in the `BunString__toJSDOMURL` function. The code path is:

1. `server.url` getter calls into the URL conversion function
2. `DOMURL::create(str, String())` returns an `ExceptionOr<Ref<DOMURL>>` — which is an exception for invalid URLs
3. `toJSNewlyCreated(...)` propagates the exception onto the throw scope and returns an empty `JSValue`
4. The code unconditionally calls `jsCast<JSDOMURL*>(jsValue.asCell())` on the null cell

The function needs to check for and handle the exception before trying to use the result value.

## Expected Behavior

Accessing `server.url` when the URL is invalid should throw a proper JavaScript error, not crash the process.
