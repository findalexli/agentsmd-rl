# Preserve Buffered Chunks on Stream Close in httpBatchStreamLink

## Problem

When a ReadableStream closes normally (not due to error), buffered chunks are being lost in the `jsonlStreamConsumer` function.

The root cause is that `packages/server/src/unstable-core-do-not-import/stream/jsonl.ts` currently uses a single handler for both stream `close` and `abort` events. This handler calls `controller.error()` on all pending controllers, which immediately discards all enqueued chunks. For normal stream completion, `controller.close()` should be used instead to preserve buffered data.

This causes data loss when the stream completes while chunks are still buffered, particularly with slow consumers or when the pipeTo pipeline completes before all chunks are read.

Reference: https://github.com/trpc/trpc/issues/7209

## Required Behavior

When the stream closes normally (without error), the following must happen:

1. If the stream closed before any head data was received, reject the pending head promise with the error message `"Stream closed before head was received"`, then clear the pending head reference (set to `null`) to prevent double-rejection

2. All stream controllers must be gracefully closed (not errored) to preserve buffered chunks. This requires a `closeAll()` method that iterates over all controllers and calls `controller.close()` on each

When the stream is aborted or cancelled:

1. Reject the pending head promise with the abort reason, then set it to `null`
2. Call `cancelAll(reason)` to error all controllers (this is the correct behavior for cancellation)

When an error occurs during stream processing (the `.catch()` block):

1. The error should be treated as an abort/cancellation scenario (not a normal close), since errors represent abnormal termination

The stream event hooks must use separate handlers:
- The `close` event must use a dedicated handler function
- The `abort` event must use a separate dedicated handler function

## Testing

Run the repository's tests with:

```bash
pnpm test --filter=@trpc/server -- jsonl.test.ts --watch=false
```

Also verify:

```bash
pnpm vitest run --project=@trpc/server
pnpm vitest run streaming.test.ts
```
