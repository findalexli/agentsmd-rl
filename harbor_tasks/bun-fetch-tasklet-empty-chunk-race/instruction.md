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

Add a guard in `FetchTasklet.zig` that prevents processing when a stale `onProgressUpdate` task finds an empty `scheduled_response_buffer` in the non-terminal success case.

The guard must:
- Check that the `scheduled_response_buffer` list items length is zero
- Check that `this.result` indicates more data is coming (`has_more` is true)
- Check that `this.result` indicates success (via `isSuccess()`)
- Be placed inside the `is_waiting_body` block, before the call to `onBodyReceived()`
- Include a comment explaining this as a "stale-task race" that references the `onStartStreamingHTTPResponseBodyCallback` callback

The terminal branch (when `has_more` is false) should NOT be affected - a zero-length final chunk is valid and should be processed normally.

## File

- `src/bun.js/webcore/fetch/FetchTasklet.zig` - Contains the streaming body handling logic
