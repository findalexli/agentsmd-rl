#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

if grep -q "isFinalized" extensions/msteams/src/reply-stream-controller.ts 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

git apply - <<'PATCH'
diff --git a/extensions/msteams/src/reply-stream-controller.ts b/extensions/msteams/src/reply-stream-controller.ts
index 20299caac6b9..f0299f14b998 100644
--- a/extensions/msteams/src/reply-stream-controller.ts
+++ b/extensions/msteams/src/reply-stream-controller.ts
@@ -35,6 +35,7 @@ export function createTeamsReplyStreamController(params: {
 
   let streamReceivedTokens = false;
   let informativeUpdateSent = false;
+  let pendingFinalize: Promise<void> | undefined;
 
   return {
     async onReplyStart(): Promise<void> {
@@ -54,10 +55,16 @@ export function createTeamsReplyStreamController(params: {
     },
 
     preparePayload(payload: ReplyPayload): ReplyPayload | undefined {
-      if (!stream || !streamReceivedTokens || !stream.hasContent) {
+      if (!stream || !streamReceivedTokens || !stream.hasContent || stream.isFinalized) {
         return payload;
       }
 
+      // Stream handled this text segment — finalize it and reset so any
+      // subsequent text segments (after tool calls) use fallback delivery.
+      // finalize() is idempotent; the later call in markDispatchIdle is a no-op.
+      streamReceivedTokens = false;
+      pendingFinalize = stream.finalize();
+
       const hasMedia = Boolean(payload.mediaUrl || payload.mediaUrls?.length);
       if (!hasMedia) {
         return undefined;
@@ -66,6 +73,7 @@ export function createTeamsReplyStreamController(params: {
     },
 
     async finalize(): Promise<void> {
+      await pendingFinalize;
       await stream?.finalize();
     },

PATCH
