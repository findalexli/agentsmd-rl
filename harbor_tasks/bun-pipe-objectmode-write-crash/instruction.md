# Bug: Uncatchable crash when piping object-mode Readable into byte-mode stream

## Summary

When a `Readable` stream in object mode is piped into a `Transform` or `Writable` that expects byte data (strings, Buffers, or TypedArrays), the destination's `write()` method throws `ERR_INVALID_ARG_TYPE`. This error is not caught — it crashes the process instead of being emitted on the destination stream's `error` event.

In Node.js, this error is caught and forwarded to the destination stream's error handler, allowing applications to handle it gracefully. Bun should match this behavior.

## Reproduction

```js
import { Readable, Transform } from "node:stream";

const objectReadable = Readable.from([{ hello: "world" }]);

const byteTransform = new Transform({
  objectMode: false,
  transform(chunk, _encoding, cb) {
    this.push(chunk);
    cb();
  },
});

byteTransform.on("error", (err) => {
  console.log("Got error on stream:", err.code);
  // Expected: "ERR_INVALID_ARG_TYPE"
  // Actual: never reached — process crashes
});

objectReadable.pipe(byteTransform);
```

## Expected behavior

- The error should be emitted on the destination stream's `error` event
- The destination stream should be destroyed with the error
- The error should be catchable via `for await` iteration as well

## Relevant code

The `Readable.prototype.pipe` implementation and its `ondata` helper function are located in `src/js/internal/streams/readable.ts`. The `ondata` function is responsible for pulling data from the readable and writing it to the destination; this is where write errors must be caught and forwarded.

## Notes

- When a stream pipe operation encounters an error during write operations, the error must be caught and forwarded to the stream's error handling mechanism, matching Node.js behavior
- Follow the existing patterns in the codebase for error handling in stream operations

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
