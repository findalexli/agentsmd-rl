# bun-fetch-tasklet-empty-chunk-race

## Problem

When using `pipeline(Readable.fromWeb(res.body), createWriteStream(out))` with Bun's fetch, the pipeline can permanently stall and then spin at 100% CPU in `waitForPromise`.

The root cause is a race condition in how body chunks are delivered:
1. HTTP thread receives body data, writes it to `scheduled_response_buffer`, and schedules an `onProgressUpdate` task
2. JavaScript touches `res.body`, which drains the buffer synchronously via `onStartStreamingHTTPResponseBodyCallback`
3. The already-queued `onProgressUpdate` task runs and finds the buffer empty
4. The code then processes a zero-length non-terminal chunk, which resolves a pending pull with length 0
5. `native-readable.ts` `handleNumberResult(0)` does not push data, leaving `node:stream` `state.reading = true` forever
6. `_read()` is never called again, and the pipeline stalls forever

## Expected Behavior

The race condition in `FetchTasklet.zig` should be prevented. When an empty non-terminal chunk arrives while the buffer has been drained by the streaming callback, processing should not continue and the pipeline should not stall.

The terminal branch (when `has_more` is false) should NOT be affected - a zero-length final chunk is valid and should be processed normally.

When fixing this, include a comment explaining the race interaction between the HTTP thread's scheduled task and the JS thread's streaming callback.

## File

- `src/bun.js/webcore/fetch/FetchTasklet.zig` - Contains the streaming body handling logic

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
