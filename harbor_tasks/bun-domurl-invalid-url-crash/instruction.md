# Bug: Crash when accessing `server.url` with invalid unix socket path

## Summary

When using `Bun.serve()` with a `unix` option that results in an unparseable URL (e.g., passing a non-string value such as the `Bun` object itself), accessing `server.url` causes a hard crash (segfault) instead of throwing a proper JavaScript error. The stringified value `"unix://[object Bun]"` is not parseable by the WHATWG URL parser.

## Relevant Code

The crash is in the C++ bindings. The function `BunString__toJSDOMURL` converts Bun strings to JavaScript DOMURL objects. The code path first calls `toJSNewlyCreated` to construct a JavaScript wrapper around the DOMURL, then uses `jsCast<JSDOMURL*>` to perform a downcast. On the success path, execution continues through `reportExtraMemoryAllocated` and `RELEASE_AND_RETURN`.

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

1. Accessing `server.url` with an invalid URL must throw a JavaScript exception instead of crashing
2. The fix must be a pure insertion — no existing lines may be modified or removed
3. The success path (through `reportExtraMemoryAllocated` and `RELEASE_AND_RETURN`) must remain reachable when the URL is valid

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier` (JS/TS/JSON/Markdown formatter)
- `typos` (spell-check)
- `clang-format` (C++ formatter)
