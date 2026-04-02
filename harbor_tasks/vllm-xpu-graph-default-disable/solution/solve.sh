#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Check if already applied
if grep -q 'VLLM_XPU_ENABLE_XPU_GRAPH' vllm/envs.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/envs.py b/vllm/envs.py
index ecd5f476a11b..a531b0e777ec 100755
--- a/vllm/envs.py
+++ b/vllm/envs.py
@@ -247,6 +247,7 @@
     VLLM_ELASTIC_EP_DRAIN_REQUESTS: bool = False
     VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS: bool = False
     VLLM_NIXL_EP_MAX_NUM_RANKS: int = 32
+    VLLM_XPU_ENABLE_XPU_GRAPH: bool = False


 def get_default_cache_root():
@@ -1648,6 +1649,10 @@
     "VLLM_NIXL_EP_MAX_NUM_RANKS": lambda: int(
         os.getenv("VLLM_NIXL_EP_MAX_NUM_RANKS", "32")
     ),
+    # Whether enable XPU graph on Intel GPU
+    "VLLM_XPU_ENABLE_XPU_GRAPH": lambda: bool(
+        int(os.getenv("VLLM_XPU_ENABLE_XPU_GRAPH", "0"))
+    ),
 }


diff --git a/vllm/platforms/xpu.py b/vllm/platforms/xpu.py
index 3d2c2cca124d..b8cab5f45dcd 100644
--- a/vllm/platforms/xpu.py
+++ b/vllm/platforms/xpu.py
@@ -12,6 +12,7 @@
 import vllm_xpu_kernels._moe_C  # noqa
 import vllm_xpu_kernels._xpu_C  # noqa

+import vllm.envs as envs
 from vllm.logger import init_logger
 from vllm.utils.torch_utils import supports_xpu_graph
 from vllm.v1.attention.backends.registry import AttentionBackendEnum
@@ -181,6 +182,12 @@
                 "XPU Graph is not supported in the current PyTorch version, "
                 "disabling cudagraph_mode."
             )
+        elif not envs.VLLM_XPU_ENABLE_XPU_GRAPH:
+            compilation_config.cudagraph_mode = CUDAGraphMode.NONE
+            logger.warning(
+                "XPU Graph is disabled by environment variable, "
+                "please set VLLM_XPU_ENABLE_XPU_GRAPH=1 to enable it."
+            )
         elif parallel_config.world_size_across_dp > 1:
             compilation_config.cudagraph_mode = CUDAGraphMode.NONE
             logger.warning(

PATCH

echo "Patch applied successfully."
