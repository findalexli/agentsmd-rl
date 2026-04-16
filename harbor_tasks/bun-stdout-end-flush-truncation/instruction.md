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

## Expected Behavior

The `.end(callback)` should only invoke the callback after all buffered data has been fully flushed through the underlying sink, matching Node.js behavior.

The fix must:

1. Ensure buffered data is flushed before the callback fires
2. Handle both synchronous and asynchronous flush completion
3. Propagate any flush errors to the callback without throwing uncaught exceptions
4. Use `$isPromise` (not `instanceof Promise`) for Promise detection
5. Use `.$call` and `.$apply` (not `.call` and `.apply`) for function invocation
6. Preserve all existing stream properties: `_destroy`, `_isStdio`, `destroySoon`, `fd`, `_type`

## Relevant Files

- The writable stream implementation for `process.stdout` and `process.stderr`
- The stream setup logic that configures `_destroy`, `_isStdio`, `destroySoon`, `fd`, and `_type` properties
- Uses the `internal/fs/streams` module and the `kWriteStreamFastPath` mechanism for fast-path writes
- Exports the `getStdioWriteStream` function for creating stdio write streams

## Technical Context

The issue involves Bun's writable stream implementation. The codebase uses:
- TypeScript files in `src/js/builtins/` with Bun's JavaScriptCore intrinsics (`$isPromise`, `.$call`, `.$apply`)
- All `require()` calls must use string literals
- Oxlint and Prettier are used for linting and formatting
