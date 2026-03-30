#!/usr/bin/env bash
set -euo pipefail
cd /workspace/vllm

if grep -q "_resolve_fi_ar_backend" vllm/distributed/device_communicators/flashinfer_all_reduce.py 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

# Change default in envs.py
sed -i "s/VLLM_FLASHINFER_ALLREDUCE_BACKEND.*=.*\"trtllm\"/VLLM_FLASHINFER_ALLREDUCE_BACKEND: Literal[\"auto\", \"trtllm\", \"mnnvl\"] = \"auto\"/" vllm/envs.py
sed -i 's/env_with_choices(\s*"VLLM_FLASHINFER_ALLREDUCE_BACKEND",\s*"trtllm"/env_with_choices("VLLM_FLASHINFER_ALLREDUCE_BACKEND", "auto"/' vllm/envs.py

git apply - <<'PATCH'
diff --git a/vllm/distributed/device_communicators/flashinfer_all_reduce.py b/vllm/distributed/device_communicators/flashinfer_all_reduce.py
index b2edfc15d731..a65789a28338 100644
--- a/vllm/distributed/device_communicators/flashinfer_all_reduce.py
+++ b/vllm/distributed/device_communicators/flashinfer_all_reduce.py
@@ -13,11 +13,13 @@
 
 import vllm.envs as envs
 from vllm.config.compilation import PassConfig
+from vllm.distributed.parallel_state import get_node_count
 from vllm.logger import init_logger
 from vllm.platforms import current_platform
 
 logger = init_logger(__name__)
 
+
 fi_ar_available = False
 try:
     import flashinfer.comm as flashinfer_comm
@@ -87,6 +89,27 @@ def _create_workspace(
     return workspace
 
 
+def _resolve_fi_ar_backend() -> str:
+    backend = envs.VLLM_FLASHINFER_ALLREDUCE_BACKEND
+    if backend != "auto":
+        logger.info_once(f"Using flashinfer allreduce backend: {backend}")
+        return backend
+
+    if get_node_count() > 1:
+        backend = "mnnvl"
+    else:
+        backend = "trtllm"
+
+    logger.info_once(f"Auto-selected flashinfer allreduce backend: {backend}")
+    return backend
+
+
 def get_fi_ar_workspace(
     world_size: int,
     rank: int,
@@ -106,7 +129,13 @@ def get_fi_ar_workspace(
     if _fi_ar_workspace is not None:
         return _fi_ar_workspace
 
-    backend = envs.VLLM_FLASHINFER_ALLREDUCE_BACKEND
+    backend = _resolve_fi_ar_backend()
+
+    if get_node_count() > 1 and backend == "trtllm":
+        raise ValueError(
+            "Flashinfer allreduce is not supported for multi-node allreduce with "
+            "'trtllm' backend. Please use 'mnnvl' backend instead."
+        )
 
     if _fi_ar_quant_workspace is not None and _fi_ar_quant_workspace.backend == backend:
         _fi_ar_workspace = _fi_ar_quant_workspace
@@ -131,6 +171,13 @@ def get_fi_ar_quant_workspace(
     if _fi_ar_quant_workspace is not None:
         return _fi_ar_quant_workspace
 
+    if get_node_count() > 1:
+        logger.warning_once(
+            "Flashinfer allreduce quantization fusion is not supported for "
+            "multi-node allreduce. Disabling quant fusion."
+        )
+        return None
+
     if _fi_ar_workspace is not None and _fi_ar_workspace.backend == "trtllm":
         _fi_ar_quant_workspace = _fi_ar_workspace
PATCH
