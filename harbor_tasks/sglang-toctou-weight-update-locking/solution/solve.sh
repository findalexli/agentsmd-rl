#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied (checking for distinctive comment from fix)
if grep -q 'Hold is_pause_cond while updating to prevent unpause from racing' python/sglang/srt/managers/tokenizer_communicator_mixin.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the TOCTOU race fix
git apply - <<'PATCH'
diff --git a/python/sglang/srt/managers/tokenizer_communicator_mixin.py b/python/sglang/srt/managers/tokenizer_communicator_mixin.py
index 76d54016869e..334caf002bdb 100644
--- a/python/sglang/srt/managers/tokenizer_communicator_mixin.py
+++ b/python/sglang/srt/managers/tokenizer_communicator_mixin.py
@@ -6,7 +6,6 @@ import asyncio
 import time
 import uuid
 from collections import deque
-from contextlib import nullcontext
 from typing import (
     TYPE_CHECKING,
     Any,
@@ -624,15 +623,15 @@ async def update_weights_from_distributed(
         if obj.abort_all_requests:
             self.abort_request(abort_all=True)

-        # Immediately update the weights if the engine is in paused state
+        # Hold is_pause_cond while updating to prevent unpause from racing.
         async with self.is_pause_cond:
             is_paused = self.is_pause
+            if is_paused:
+                results = await self.update_weights_from_distributed_communicator(obj)

-        lock_context = (
-            self.model_update_lock.writer_lock if not is_paused else nullcontext()
-        )
-        async with lock_context:
-            results = await self.update_weights_from_distributed_communicator(obj)
+        if not is_paused:
+            async with self.model_update_lock.writer_lock:
+                results = await self.update_weights_from_distributed_communicator(obj)

         success, message = _Communicator.merge_results(results)
         if success and obj.weight_version is not None:
@@ -682,15 +681,14 @@ async def update_weights_from_tensor(
         if obj.abort_all_requests:
             self.abort_request(abort_all=True)

-        # Immediately update the weights if the engine is in paused state
         async with self.is_pause_cond:
             is_paused = self.is_pause
+            if is_paused:
+                results = await self.update_weights_from_tensor_communicator(obj)

-        lock_context = (
-            self.model_update_lock.writer_lock if not is_paused else nullcontext()
-        )
-        async with lock_context:
-            results = await self.update_weights_from_tensor_communicator(obj)
+        if not is_paused:
+            async with self.model_update_lock.writer_lock:
+                results = await self.update_weights_from_tensor_communicator(obj)

         success, message = _Communicator.merge_results(results)
         if success and obj.weight_version is not None:
@@ -713,19 +711,16 @@ async def update_weights_from_ipc(
             ), "dp_size must be 1 or dp attention must be enabled for update weights from IPC"
             logger.info("Starting IPC weight update")

-            # Skip the writer lock when paused: readers are blocked on
-            # is_pause_cond so no concurrent inference can race, and
-            # waiting for the writer lock would deadlock because existing
-            # readers are stuck waiting on the paused scheduler.
             async with self.is_pause_cond:
                 is_paused = self.is_pause
-
-            lock_context = (
-                self.model_update_lock.writer_lock if not is_paused else nullcontext()
-            )
-            async with lock_context:
-                result = (await self.update_weights_from_ipc_communicator(obj))[0]
-                success, message = result.success, result.message
+                if is_paused:
+                    result = (await self.update_weights_from_ipc_communicator(obj))[0]
+                    success, message = result.success, result.message
+
+            if not is_paused:
+                async with self.model_update_lock.writer_lock:
+                    result = (await self.update_weights_from_ipc_communicator(obj))[0]
+                    success, message = result.success, result.message
         except Exception as e:
             error_msg = f"IPC weight update failed: {str(e)}"
             logger.error(error_msg)

PATCH

echo "Patch applied successfully."
