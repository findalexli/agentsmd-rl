#!/usr/bin/env bash
set -euo pipefail
cd /workspace/slime

git apply - <<'PATCH'
diff --git a/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py b/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py
index b53cc5bdc..dbba6aeb5 100644
--- a/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py
+++ b/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py
@@ -158,9 +158,16 @@ def update_weights(self) -> None:
         for hf_named_tensors in self._hf_weight_iterator.get_hf_weight_chunks(megatron_local_weights):
             refs, long_lived_tensors = self._send_hf_params(hf_named_tensors)
             ray.get(refs)
-            del long_lived_tensors
+            # Free GPU tensors so the caching allocator can reuse the blocks,
+            # then release CUDA IPC cache entries whose consumers (sglang engines)
+            # have already closed their IPC handles.
+            del long_lived_tensors, hf_named_tensors
+            torch.cuda.ipc_collect()

         dist.barrier(group=get_gloo_group())
+        # After the barrier all engines have returned, so every rank's last-chunk
+        # IPC handles are now released by the consumers.  Clean them up.
+        torch.cuda.ipc_collect()

         # int4/fp4 post_process
         if rank == 0:
@@ -212,7 +219,6 @@ def _send_to_colocated_engine(
     if ipc_gather_group is None:
         return [], None

-    # TODO improve
     long_live_tensors = []

     if getattr(FlattenedTensorBucket, "supports_multi_dtypes", False):
PATCH
