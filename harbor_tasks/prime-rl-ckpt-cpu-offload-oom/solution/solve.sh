#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied
if grep -q 'gc.collect()' src/prime_rl/trainer/ckpt.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/trainer/ckpt.py b/src/prime_rl/trainer/ckpt.py
index 4734cfc563..296554e0e8 100644
--- a/src/prime_rl/trainer/ckpt.py
+++ b/src/prime_rl/trainer/ckpt.py
@@ -1,4 +1,5 @@
 import bisect
+import gc
 import shutil
 import time
 import warnings
@@ -101,10 +102,12 @@ def load_state_dict(self, state_dict: dict[str, Any]):
         )

         # Re-initialize CPU offload wrappers after loading
+        has_cpu_offload = False
         for opt in self.optimizers:
             if isinstance(opt, CPUOffloadOptimizer):
                 opt._move_states("cpu")
                 opt._initialized = True
+                has_cpu_offload = True

         if self.scheduler is not None:
             self.scheduler.load_state_dict(state_dict["scheduler"])
@@ -112,6 +115,16 @@ def load_state_dict(self, state_dict: dict[str, Any]):
             for key, value in state_dict["progress"].items():
                 setattr(self.progress, key, value)

+        # Reclaim GPU memory freed by moving optimizer states to CPU.
+        # After set_state_dict + _move_states("cpu"), the optimizer states live on CPU,
+        # but the state_dict (owned by dcp_load) still holds references to stale GPU
+        # optimizer tensors. Clearing them and flushing the CUDA cache prevents OOM on
+        # the first training step.
+        if has_cpu_offload:
+            state_dict.clear()  # drop stale GPU tensor references from dcp_load
+            gc.collect()  # break any circular references so tensors are freed
+            torch.cuda.empty_cache()  # return freed GPU memory to CUDA
+

 class CheckpointManager:
     """Utility class to save and load trainer checkpoints to resume SFT and RL training."""

PATCH

echo "Patch applied successfully."
