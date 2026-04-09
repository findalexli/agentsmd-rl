#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied
if grep -q 'Skip the writer lock when paused' python/sglang/srt/managers/tokenizer_communicator_mixin.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/python/sglang/srt/managers/tokenizer_communicator_mixin.py b/python/sglang/srt/managers/tokenizer_communicator_mixin.py
index 8ba0fe0772e5..6d54016869e2 100644
--- a/python/sglang/srt/managers/tokenizer_communicator_mixin.py
+++ b/python/sglang/srt/managers/tokenizer_communicator_mixin.py
@@ -712,8 +712,18 @@ async def update_weights_from_ipc(
                 self.server_args.dp_size == 1 or self.server_args.enable_dp_attention
             ), "dp_size must be 1 or dp attention must be enabled for update weights from IPC"
             logger.info("Starting IPC weight update")
-            # This means that weight sync cannot run while requests are in progress.
-            async with self.model_update_lock.writer_lock:
+
+            # Skip the writer lock when paused: readers are blocked on
+            # is_pause_cond so no concurrent inference can race, and
+            # waiting for the writer lock would deadlock because existing
+            # readers are stuck waiting on the paused scheduler.
+            async with self.is_pause_cond:
+                is_paused = self.is_pause
+
+            lock_context = (
+                self.model_update_lock.writer_lock if not is_paused else nullcontext()
+            )
+            async with lock_context:
                 result = (await self.update_weights_from_ipc_communicator(obj))[0]
                 success, message = result.success, result.message
         except Exception as e:

PATCH

echo "Patch applied successfully."
