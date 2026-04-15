# Bug: process.stdout.end() callback fires before data is fully flushed

## Summary

When writing large amounts of data to `process.stdout` and then calling `.end(callback)`, the callback fires prematurely — before all buffered data has been flushed through the pipe. This causes output truncation at power-of-2 boundaries (64KB, 128KB, etc.) when the callback calls `process.exit(0)`.

## Reproduction

```js
const output = Buffer.alloc(200000, 120).toString() + "\n";
process.stdout.write(output);
process.stdout.end(() => { process.exit(0); });
```

When piping to another process:
```
$ bun repro.js | wc -c
65536          # expected: 200001
```

Node.js outputs all 200001 bytes correctly in the same scenario.

## Analysis

The issue is in the writable stream implementation used for `process.stdout` and `process.stderr`. These streams use a fast-path write mechanism that bypasses `Writable._writableState` tracking — it never updates `pendingcb`. When `.end()` is called, the internal `finishMaybe()` sees `pendingcb === 0` and immediately schedules the finish callback, even though the underlying file sink may still have buffered data waiting to be flushed through the pipe.

## Expected Behavior

The `.end(callback)` should only invoke the callback after all buffered data has been fully flushed through the underlying sink, matching Node.js behavior.

The stream's completion mechanism must:

1. Call `sink.flush()` to flush any pending data through the underlying file descriptor
2. Handle synchronous flush completion by invoking the callback with `null` or `undefined`
3. Handle asynchronous flush completion by detecting when `sink.flush()` returns a Promise, waiting for it to resolve before invoking the callback with `null` or `undefined`
4. Propagate any errors from the flush operation to the callback without throwing uncaught exceptions
5. Use `$isPromise` (not `instanceof Promise`) for Promise detection
6. Use `.$call` and `.$apply` (not `.call` and `.apply`) for function invocation

## Relevant Files

- `src/js/builtins/ProcessObjectInternals.ts` — contains the stream creation logic for stdio
- Look for references to `kWriteStreamFastPath` and `internal/fs/streams` module usage
