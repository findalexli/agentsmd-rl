# bun-fetch-tasklet-empty-chunk-race

## Problem

When using `pipeline(Readable.fromWeb(res.body), createWriteStream(out))` with Bun's fetch, the pipeline can permanently stall and then spin at 100% CPU in `waitForPromise`. This happens due to a race condition between the HTTP thread delivering body chunks and the JavaScript thread accessing `res.body`.

The race occurs as follows:
1. HTTP thread receives the first body chunk and enqueues an `onProgressUpdate` task
2. JS touches `res.body`, which calls `onStartStreamingHTTPResponseBodyCallback` and drains the buffer
3. The already-queued `onProgressUpdate` task runs but finds the buffer empty
4. Without a guard, `onBodyReceived` calls `ByteStream.onData` with a zero-length non-terminal chunk
5. This resolves the pending pull with `len=0`, but `handleNumberResult(0)` doesn't push, leaving `node:stream` `state.reading = true` forever
6. `_read()` is never called again, and the pipeline stalls forever

## Expected Behavior

The fix should skip calling `ByteStream.onData` when the scheduled response buffer is empty, `has_more` is true, and the result is successful. This prevents the zero-length chunk from consuming the pending pull and stalling the stream.

## Files to Look At

- `src/bun.js/webcore/fetch/FetchTasklet.zig` — Contains the `onBodyReceived` logic that needs the guard

## Hints

- Look for the `is_waiting_body` block in the task callback
- The guard should check three conditions: empty buffer, `has_more` flag, and success status
- The fix includes an extensive comment explaining the stale-task race - read it carefully
- The terminal (`!has_more`) branch should NOT be affected - a zero-length final chunk is valid
