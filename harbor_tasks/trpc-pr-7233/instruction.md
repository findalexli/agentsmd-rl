# Task: Fix Buffered Chunks Discarded on Stream Close

## Problem Description

In `httpBatchStreamLink`, when a stream completes normally (not aborted), any buffered chunks are silently discarded. This happens because the `close` and `abort` handlers both call `controller.error()`.

Per the [WHATWG Streams spec](https://streams.spec.whatwg.org/#rs-default-controller-error), `controller.error()` immediately transitions the stream to "errored" state and **discards all enqueued chunks**.

## Expected Behavior

When a stream closes normally (not aborted), all buffered chunks should be delivered to the consumer. The stream should transition to "closed" state via `controller.close()`, not "errored" state via `controller.error()`.

## Symptoms

1. **Data Loss on Normal Completion**: When iterating over a stream that yields multiple values rapidly (e.g., `[0, 1, 2, 3, 4]`), only some values are received before the stream closes. Buffered values are lost.

2. **Non-descriptive Error on Premature Close**: When a `ReadableStream` closes before emitting any head data, `jsonlStreamConsumer` rejects with `undefined` instead of a descriptive `Error` object. The expected error message is: `"Stream closed before head was received"`.

## Files to Investigate

- `packages/server/src/unstable-core-do-not-import/stream/jsonl.ts` — contains `jsonlStreamConsumer` and `createStreamsManager`
- `packages/server/src/unstable-core-do-not-import/stream/jsonl.test.ts` — existing tests for the stream module

## Test Verification

After making your fix, run:
```bash
pnpm vitest run packages/server/src/unstable-core-do-not-import/stream/jsonl.test.ts
```

Your fix should make both of these regression tests pass:
- `buffered chunks preserved on normal stream completion` — verifies all 5 values `[0, 1, 2, 3, 4]` are received
- `stream closing before head rejects headDeferred with descriptive error` — verifies rejection is an `Error` with message `"Stream closed before head was received"`