#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q "stale-task race" src/bun.js/webcore/fetch/FetchTasklet.zig 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/src/bun.js/webcore/fetch/FetchTasklet.zig b/src/bun.js/webcore/fetch/FetchTasklet.zig
index 1a3b39b4a54..6eb773092a2 100644
--- a/src/bun.js/webcore/fetch/FetchTasklet.zig
+++ b/src/bun.js/webcore/fetch/FetchTasklet.zig
@@ -483,6 +483,35 @@ pub const FetchTasklet = struct {
         }
         // if we already respond the metadata and still need to process the body
         if (this.is_waiting_body) {
+            // `scheduled_response_buffer` has two readers that both drain-and-reset:
+            // this path (onBodyReceived) and `onStartStreamingHTTPResponseBodyCallback`,
+            // which runs once when JS first touches `res.body` and hands any already-
+            // buffered bytes to the new ByteStream synchronously.
+            //
+            // That creates a stale-task race:
+            //   1. HTTP thread `callback()` writes N bytes to the buffer and enqueues
+            //      this onProgressUpdate task (under mutex).
+            //   2. Main thread: JS touches `res.body` -> `onStartStreaming` drains those
+            //      N bytes and resets the buffer (under mutex).
+            //   3. This task runs and finds the buffer empty.
+            //
+            // The task cannot be un-enqueued in step 2, and at schedule time (step 1)
+            // the buffer was non-empty, so the only place the staleness is observable
+            // is here when the task runs.
+            //
+            // Without this guard, `onBodyReceived` would call `ByteStream.onData` with
+            // a zero-length non-terminal chunk. That resolves the reader's pending
+            // pull with `len=0`; `native-readable.ts` `handleNumberResult(0)` does not
+            // `push()`, so node:stream `state.reading` (set before the previous `_read()`
+            // early-returned on `kPendingRead`) is never cleared, `_read()` is never
+            // called again, and `pipeline(Readable.fromWeb(res.body), ...)` stalls
+            // forever — eventually spinning at 100% CPU once `poll_ref` unrefs.
+            if (this.scheduled_response_buffer.list.items.len == 0 and
+                this.result.has_more and
+                this.result.isSuccess())
+            {
+                return;
+            }
             try this.onBodyReceived();
             return;
         }

PATCH

echo "Patch applied successfully."
