#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotency check: if CpuPlatform already has memory_allocated, patch was applied
if grep -q 'def memory_allocated' areal/infra/platforms/cpu.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/engine/fsdp_engine.py b/areal/engine/fsdp_engine.py
index ccc4a7867..276ce2277 100644
--- a/areal/engine/fsdp_engine.py
+++ b/areal/engine/fsdp_engine.py
@@ -777,7 +777,10 @@ def _create_llm_actor_or_critic(self):

     def _create_device_model(self):
         current_platform.set_device(int(os.environ["LOCAL_RANK"]))
-        self.device = torch.device(int(os.environ["LOCAL_RANK"]))
+        if current_platform.device_type == "cpu":
+            self.device = torch.device("cpu")
+        else:
+            self.device = torch.device(int(os.environ["LOCAL_RANK"]))

         dtype = getattr(torch, self.config.dtype)

diff --git a/areal/experimental/engine/archon_engine.py b/areal/experimental/engine/archon_engine.py
index 5a885a6ea..38511d699 100644
--- a/areal/experimental/engine/archon_engine.py
+++ b/areal/experimental/engine/archon_engine.py
@@ -938,7 +938,10 @@ def _get_model_name_parameters(self) -> Iterator[tuple[str, nn.Parameter]]:

     def _create_device_model(self):
         current_platform.set_device(int(os.environ["LOCAL_RANK"]))
-        self.device = torch.device(int(os.environ["LOCAL_RANK"]))
+        if current_platform.device_type == "cpu":
+            self.device = torch.device("cpu")
+        else:
+            self.device = torch.device(int(os.environ["LOCAL_RANK"]))

         self.tokenizer = load_hf_tokenizer(self.config.path)

diff --git a/areal/infra/platforms/cpu.py b/areal/infra/platforms/cpu.py
index 20d19d6bd..8c4f08d22 100644
--- a/areal/infra/platforms/cpu.py
+++ b/areal/infra/platforms/cpu.py
@@ -36,3 +36,19 @@ def update_env_vars_for_visible_devices(
     def get_visible_devices(cls) -> list:
         # No-devices for CPU platform
         return []
+
+    def memory_allocated(self) -> int:
+        """No device memory; return 0."""
+        return 0
+
+    def memory_reserved(self) -> int:
+        """No device memory; return 0."""
+        return 0
+
+    def mem_get_info(self) -> tuple[int, int]:
+        """No device memory; return (0, 0)."""
+        return (0, 0)
+
+    def empty_cache(self) -> None:
+        """No-op."""
+        pass
diff --git a/areal/infra/scheduler/local.py b/areal/infra/scheduler/local.py
index a90cf48a1..f74bb6c2a 100644
--- a/areal/infra/scheduler/local.py
+++ b/areal/infra/scheduler/local.py
@@ -630,9 +630,10 @@ def create_workers(self, job: Job, *args, **kwargs) -> list[str]:
                 env = get_env_vars(
                     ",".join([f"{k}={v}" for k, v in scheduling.env_vars.items()]),
                 )
-                env[current_platform.device_control_env_var] = ",".join(
-                    map(str, gpu_devices)
-                )
+                if current_platform.device_control_env_var:
+                    env[current_platform.device_control_env_var] = ",".join(
+                        map(str, gpu_devices)
+                    )

                 thread_env = get_thread_env_vars(
                     cpus_per_task=scheduling.cpu,

PATCH

echo "Patch applied successfully."
