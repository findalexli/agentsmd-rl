#!/usr/bin/env bash
set -euo pipefail

# Idempotency check: if set_numa_affinity already exists in cuda.py, patch was applied
if grep -q 'def set_numa_affinity' areal/infra/platforms/cuda.py; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/engine/fsdp_engine.py b/areal/engine/fsdp_engine.py
index 752e95978..151020f8b 100644
--- a/areal/engine/fsdp_engine.py
+++ b/areal/engine/fsdp_engine.py
@@ -804,6 +804,7 @@ def _create_llm_actor_or_critic(self):

     def _create_device_model(self):
         current_platform.set_device(int(os.environ["LOCAL_RANK"]))
+        current_platform.set_numa_affinity(int(os.environ["LOCAL_RANK"]))
         if current_platform.device_type == "cpu":
             self.device = torch.device("cpu")
         else:
diff --git a/areal/engine/megatron_engine.py b/areal/engine/megatron_engine.py
index a7055f16e..78d24a53d 100644
--- a/areal/engine/megatron_engine.py
+++ b/areal/engine/megatron_engine.py
@@ -222,6 +222,7 @@ def initialize(self, addr: str | None, ft_spec: FinetuneSpec, *args, **kwargs):
             torch_memory_saver.hook_mode = "preload"

         current_platform.set_device(int(os.environ["LOCAL_RANK"]))
+        current_platform.set_numa_affinity(int(os.environ["LOCAL_RANK"]))
         self.device = torch.device(int(os.environ["LOCAL_RANK"]))
         self.rank = int(os.environ["RANK"])
         self.world_size = int(os.environ["WORLD_SIZE"])
diff --git a/areal/experimental/engine/archon_engine.py b/areal/experimental/engine/archon_engine.py
index 48b9b8f7e..c0999d319 100644
--- a/areal/experimental/engine/archon_engine.py
+++ b/areal/experimental/engine/archon_engine.py
@@ -938,6 +938,7 @@ def _get_model_name_parameters(self) -> Iterator[tuple[str, nn.Parameter]]:

     def _create_device_model(self):
         current_platform.set_device(int(os.environ["LOCAL_RANK"]))
+        current_platform.set_numa_affinity(int(os.environ["LOCAL_RANK"]))
         if current_platform.device_type == "cpu":
             self.device = torch.device("cpu")
         else:
diff --git a/areal/infra/platforms/cuda.py b/areal/infra/platforms/cuda.py
index 8da2e54e8..db9117dd4 100644
--- a/areal/infra/platforms/cuda.py
+++ b/areal/infra/platforms/cuda.py
@@ -1,4 +1,5 @@
 import gc
+import os

 import torch

@@ -56,6 +57,34 @@ def get_vllm_worker_class(clas):
     def set_allocator_settings(cls) -> None:
         torch.cuda.memory._set_allocator_settings("expandable_segments:False")

+    @classmethod
+    def set_numa_affinity(cls, local_rank: int) -> None:
+        """Bind the current process to CPU cores local to the assigned GPU."""
+
+        nvml_initialized = False
+        try:
+            import pynvml
+
+            pynvml.nvmlInit()
+            nvml_initialized = True
+            handle = pynvml.nvmlDeviceGetHandleByIndex(local_rank)
+            pynvml.nvmlDeviceSetCpuAffinity(handle)
+            cpu_set = os.sched_getaffinity(0)
+            logger.info(
+                "Set NUMA affinity for GPU %s: bound to %s CPU cores.",
+                local_rank,
+                len(cpu_set),
+            )
+        except ImportError:
+            logger.warning(
+                "pynvml (nvidia-ml-py) not available, skipping NUMA affinity setup."
+            )
+        except Exception as e:
+            logger.warning("Failed to set NUMA affinity for GPU %s: %s", local_rank, e)
+        finally:
+            if nvml_initialized:
+                pynvml.nvmlShutdown()
+
     @classmethod
     def get_custom_env_vars(cls) -> dict:
         env_vars = {
diff --git a/areal/infra/platforms/platform.py b/areal/infra/platforms/platform.py
index 63d3e5d18..c3a2f8eed 100644
--- a/areal/infra/platforms/platform.py
+++ b/areal/infra/platforms/platform.py
@@ -102,6 +102,11 @@ def set_allocator_settings(cls) -> None:
         """Configure memory allocator settings based on the device type."""
         raise NotImplementedError()

+    @classmethod
+    def set_numa_affinity(cls, local_rank: int) -> None:
+        """Bind the current process to CPU cores near the assigned device."""
+        return
+
     @classmethod
     def get_custom_env_vars(cls) -> dict:
         """

PATCH

echo "Patch applied successfully."
