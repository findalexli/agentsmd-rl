# Bug: Crash when consuming Response body created from async iterable

## Summary

When a `Response` object is constructed with a body backed by an async iterable (`Symbol.asyncIterator`), calling `.bytes()` or `.arrayBuffer()` on it crashes with a null dereference error ("null is not an object"). Additionally, calling the same consumption method a second time does not properly reject — the stream is not locked after the first consumption begins.

## Reproduction

```javascript
function* gen() {}
const body = {};
body[Symbol.asyncIterator] = () => gen();
const resp = new Response(body);

// First call crashes with null dereference
try { await resp.bytes(); } catch {}

// Second call should be rejected (stream already consumed) but isn't properly locked
try { await resp.bytes(); } catch(e) { console.log(e.message); }
```

## Root Cause

The issue spans both the JavaScript builtins and the C++ binding layer:

1. **JavaScript builtins** (`src/js/builtins/ReadableStream.ts`): The functions `readableStreamToArray`, `readableStreamToText`, `readableStreamToArrayBuffer`, and `readableStreamToBytes` check `underlyingSource` to determine if the stream is a "direct stream". However, the `initializeArrayBufferStream` function (in `ReadableStreamInternals.ts`) sets `underlyingSource` to `null` — not `undefined`. The current comparison operator does not exclude `null`, so `null` is passed to the direct-stream consumption path, which tries to access properties on it (e.g., `.pull`).

2. **JavaScript builtins** (`src/js/builtins/ReadableStreamInternals.ts`): The `onCloseDirectStream` and `onFlushDirectStream` functions access `this.$sink` without checking if it's already been cleaned up (set to `undefined`). Other error-handling paths in the same file (e.g., `handleDirectStreamError`) already have this guard. Also, `readableStreamToArrayBufferDirect` does not lock the stream, so a second consumption call bypasses the lock check.

3. **C++ layer** (`src/bun.js/bindings/webcore/ReadableStream.cpp`): Several C++ wrapper functions that call JavaScript builtins via `call()` do not check for exceptions afterward. If the JS call throws, the exception goes unhandled, which can trigger assertion failures in debug builds.

## Files to Investigate

- `src/js/builtins/ReadableStream.ts` — the four `readableStreamTo*` functions with the null-check issue
- `src/js/builtins/ReadableStreamInternals.ts` — `onCloseDirectStream`, `onFlushDirectStream`, and `readableStreamToArrayBufferDirect`
- `src/bun.js/bindings/webcore/ReadableStream.cpp` — C++ wrappers that call JS builtins
