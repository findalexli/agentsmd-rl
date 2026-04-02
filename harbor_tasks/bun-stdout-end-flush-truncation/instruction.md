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

The issue is in `src/js/builtins/ProcessObjectInternals.ts`, in the `getStdioWriteStream` function.

`process.stdout` uses a fast-path write mechanism that bypasses `Writable._writableState` tracking — it never updates `pendingcb`. When `.end()` is called, the internal `finishMaybe()` sees `pendingcb === 0` and immediately schedules the finish callback, even though the underlying file sink may still have buffered data waiting to be flushed through the pipe.

The stream lacks a `_final` hook. In Node.js streams, `_final` runs before the stream transitions to "finished" state, giving an opportunity to flush pending data. Without it, `.end()` completes immediately regardless of pending writes.

## Expected Behavior

The `.end(callback)` should only invoke the callback after all buffered data has been fully flushed through the underlying sink, matching Node.js behavior.

## Relevant Files

- `src/js/builtins/ProcessObjectInternals.ts` — the `getStdioWriteStream` function that creates `process.stdout` and `process.stderr` streams
