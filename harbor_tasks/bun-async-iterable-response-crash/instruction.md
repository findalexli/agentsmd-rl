# Bug: Crash when consuming Response body created from async iterable

## Summary

When a `Response` object is constructed with a body backed by an async iterable (`Symbol.asyncIterator`), calling `.bytes()` or `.arrayBuffer()` on it crashes with a "null is not an object" error. Additionally, calling the same consumption method a second time does not properly reject. In debug builds, unhandled exceptions cause assertion failures.

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

## Observed Behavior

Three distinct problems manifest when consuming Response bodies backed by async iterables:

1. **Null dereference crash**: The first call to `.bytes()` or `.arrayBuffer()` crashes with a "null is not an object" error. This occurs because the async iterable path sets an internal property to `null` rather than `undefined`, and the subsequent check in the consumption functions does not account for this distinction.

2. **Double consumption not prevented**: After a first (failing) consumption attempt, a second call to the same method should reject with an error indicating the stream is already in use, but it proceeds without rejection. The direct consumption path does not properly mark the stream as consumed.

3. **Unhandled exceptions in C++ bindings**: In debug builds, assertion failures occur because exceptions thrown during JavaScript-to-C++ boundary crossings are not properly caught. The C++ wrapper functions that call into JavaScript builtins do not check for pending exceptions after the call returns.

## Relevant Files

The implementation of ReadableStream consumption spans these files:

- `src/js/builtins/ReadableStream.ts` — contains the `readableStreamToArray`, `readableStreamToText`, `readableStreamToArrayBuffer`, and `readableStreamToBytes` functions
- `src/js/builtins/ReadableStreamInternals.ts` — contains `onCloseDirectStream`, `onFlushDirectStream`, and `readableStreamToArrayBufferDirect`
- `src/bun.js/bindings/webcore/ReadableStream.cpp` — contains C++ wrappers `readableStreamToText`, `readableStreamToFormData`, `readableStreamToJSON`, and `readableStreamToBlob`

## Code Style Requirements

- TypeScript type-checking must pass (`tsc --noEmit`).
- The repo's ban-words test (`test/internal/ban-words.test.ts`) must pass; it forbids bare `.call()`/`.apply()`, dynamic `require()`, `== undefined`/`!= undefined`, bare `.jsBoolean()`, and `std.debug.*` in builtins.
