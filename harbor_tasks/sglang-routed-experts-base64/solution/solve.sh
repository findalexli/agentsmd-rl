#!/usr/bin/env bash
set -euo pipefail
cd /workspace/sglang

# Idempotent: skip if already applied
grep -q 'isinstance(image_path, torch.Tensor)' python/sglang/utils.py && exit 0

git apply - <<'PATCH'
diff --git a/python/sglang/srt/managers/detokenizer_manager.py b/python/sglang/srt/managers/detokenizer_manager.py
index 30f804bea20d..ce27113845c7 100644
--- a/python/sglang/srt/managers/detokenizer_manager.py
+++ b/python/sglang/srt/managers/detokenizer_manager.py
@@ -21,7 +21,6 @@
 from typing import Dict, List, Optional, Tuple, Union

 import psutil
-import pybase64
 import setproctitle
 import zmq

@@ -319,21 +318,6 @@ def _decode_batch_token_id_output(self, recv_obj: BatchTokenIDOutput):

         return output_strs

-    def _extract_routed_experts(
-        self, recv_obj: BatchTokenIDOutput
-    ) -> list[str | None] | None:
-        routed_experts = None
-        if recv_obj.routed_experts is not None:
-            routed_experts = [
-                (
-                    pybase64.b64encode(routed_experts.numpy().tobytes()).decode("utf-8")
-                    if routed_experts is not None
-                    else None
-                )
-                for routed_experts in recv_obj.routed_experts
-            ]
-        return routed_experts
-
     def handle_batch_token_id_out(self, recv_obj: BatchTokenIDOutput):
         # If handling idle batch, set output_strs to [].
         output_strs = (
@@ -341,8 +325,6 @@ def handle_batch_token_id_out(self, recv_obj: BatchTokenIDOutput):
             if len(recv_obj.rids) > 0
             else []
         )
-        routed_experts = self._extract_routed_experts(recv_obj)
-
         return BatchStrOutput(
             rids=recv_obj.rids,
             http_worker_ipcs=recv_obj.http_worker_ipcs,
@@ -370,7 +352,7 @@ def handle_batch_token_id_out(self, recv_obj: BatchTokenIDOutput):
             output_token_ids_logprobs_idx=recv_obj.output_token_ids_logprobs_idx,
             output_token_entropy_val=recv_obj.output_token_entropy_val,
             output_hidden_states=recv_obj.output_hidden_states,
-            routed_experts=routed_experts,
+            routed_experts=recv_obj.routed_experts,
             customized_info=recv_obj.customized_info,
             placeholder_tokens_idx=None,
             placeholder_tokens_val=None,
diff --git a/python/sglang/srt/managers/tokenizer_manager.py b/python/sglang/srt/managers/tokenizer_manager.py
index 3c1bec753100..163ff3ab9458 100644
--- a/python/sglang/srt/managers/tokenizer_manager.py
+++ b/python/sglang/srt/managers/tokenizer_manager.py
@@ -32,6 +32,7 @@
 from typing import Any, Awaitable, Dict, List, Optional, Tuple, Union

 import fastapi
+import pybase64
 import uvloop
 import zmq
 import zmq.asyncio
@@ -1597,7 +1598,11 @@ def _handle_batch_output(
             if getattr(recv_obj, "output_hidden_states", None):
                 meta_info["hidden_states"] = recv_obj.output_hidden_states[i]
             if getattr(recv_obj, "routed_experts", None):
-                meta_info["routed_experts"] = recv_obj.routed_experts[i]
+                routed_experts_tensor = recv_obj.routed_experts[i]
+                if routed_experts_tensor is not None:
+                    meta_info["routed_experts"] = pybase64.b64encode(
+                        routed_experts_tensor.numpy().tobytes()
+                    ).decode("utf-8")
             if getattr(recv_obj, "customized_info", None):
                 for k, v in recv_obj.customized_info.items():
                     meta_info[k] = v[i]
diff --git a/python/sglang/srt/utils/numa_utils.py b/python/sglang/srt/utils/numa_utils.py
index 5c801679b716..cabba3bc499c 100644
--- a/python/sglang/srt/utils/numa_utils.py
+++ b/python/sglang/srt/utils/numa_utils.py
@@ -155,7 +155,7 @@ def _is_numa_available() -> bool:
         return False

     if not shutil.which("numactl") and envs.SGLANG_NUMA_BIND_V2.get():
-        logger.warning(
+        logger.debug(
             "numactl command not found, skipping NUMA node configuration for GPU. Install numactl (e.g., apt-get install numactl) to enable automatic NUMA binding."
         )
         return False
diff --git a/python/sglang/utils.py b/python/sglang/utils.py
index 7fac74d65d84..cd7fbe7214cc 100644
--- a/python/sglang/utils.py
+++ b/python/sglang/utils.py
@@ -204,7 +204,16 @@ def encode_image_base64(image_path: Union[str, bytes]):
     elif isinstance(image_path, bytes):
         return pybase64.b64encode(image_path).decode("utf-8")
     else:
-        # image_path is PIL.WebPImagePlugin.WebPImageFile
+        import torch
+
+        if isinstance(image_path, torch.Tensor):
+            # Convert GPU-decoded image tensor (C, H, W) uint8 to PIL Image
+            from PIL import Image
+
+            tensor = image_path.cpu() if image_path.device.type != "cpu" else image_path
+            image_path = Image.fromarray(tensor.permute(1, 2, 0).numpy())
+
+        # image_path is a PIL Image
         image = image_path
         buffered = BytesIO()
         image.save(buffered, format="PNG")

PATCH
