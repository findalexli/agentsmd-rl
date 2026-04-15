# bun-fetch-tasklet-empty-chunk-race

## Problem

When using `pipeline(Readable.fromWeb(res.body), createWriteStream(out))` with Bun's fetch, the pipeline can permanently stall and then spin at 100% CPU in `waitForPromise`.

The root cause is a race condition in how body chunks are delivered:
1. HTTP thread receives body data, writes it to a buffer, and schedules an `onProgressUpdate` task
2. JavaScript touches `res.body`, which drains the buffer synchronously via `onStartStreamingHTTPResponseBodyCallback`
3. The already-queued `onProgressUpdate` task runs and finds the buffer empty
4. The code then processes a zero-length non-terminal chunk, which resolves a pending pull with length 0
5. `native-readable.ts` `handleNumberResult(0)` does not push data, leaving `node:stream` `state.reading = true` forever
6. `_read()` is never called again, and the pipeline stalls forever

## Expected Behavior

Add a guard that prevents processing when a stale task finds an empty buffer in the non-terminal (has_more) success case. The guard should be placed before calling the body-received callback.

The fix must include a comment explaining this as a "stale-task race" and reference the `onStartStreamingHTTPResponseBodyCallback` callback. The guard must check three conditions:
- The scheduled response buffer is empty: `scheduled_response_buffer.list.items.len == 0`
- The result indicates more data is coming: `this.result.has_more`
- The result indicates success: `this.result.isSuccess()`

The terminal branch (`!has_more`) should NOT be affected - a zero-length final chunk is valid and should be processed normally.

## File

- `src/bun.js/webcore/fetch/FetchTasklet.zig` - Contains the streaming body handling logic that needs the guard
