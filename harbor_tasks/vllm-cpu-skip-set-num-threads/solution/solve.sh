#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotency check: skip if already applied
if grep -q 'skip_set_num_threads' vllm/v1/worker/cpu_worker.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/v1/worker/cpu_worker.py b/vllm/v1/worker/cpu_worker.py
index 122cacd14cd8..2547751c0d81 100644
--- a/vllm/v1/worker/cpu_worker.py
+++ b/vllm/v1/worker/cpu_worker.py
@@ -108,6 +108,15 @@ def check_preloaded_libs(name: str):
             if ret:
                 logger.info(ret)

+        # After the thread binding, changing thread num is not allowed
+        def skip_set_num_threads(x: int):
+            logger.warning(
+                "CPU backend doesn't allow to use "
+                "`torch.set_num_threads` after the thread binding, skip it."
+            )
+
+        torch.set_num_threads = skip_set_num_threads
+
         # Note: unique identifier for creating allreduce shared memory
         os.environ["VLLM_DIST_IDENT"] = self.distributed_init_method.split(":")[-1]
         # Initialize the distributed environment.

PATCH

echo "Patch applied successfully."
