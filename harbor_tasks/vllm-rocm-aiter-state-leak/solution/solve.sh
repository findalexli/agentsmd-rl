#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotency: check if the fix is already applied
if grep -q 'rocm_aiter_ops.refresh_env_variables' vllm/distributed/parallel_state.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/tests/kernels/moe/test_routing_simulator.py b/tests/kernels/moe/test_routing_simulator.py
index c0c3a1e1da9e..4ef984a3296b 100644
--- a/tests/kernels/moe/test_routing_simulator.py
+++ b/tests/kernels/moe/test_routing_simulator.py
@@ -125,8 +125,15 @@ def test_routing_strategy_integration(monkeypatch, device):
             env_name = "VLLM_MOE_ROUTING_SIMULATION_STRATEGY"
             monkeypatch.setenv(env_name, strategy)

-            # Force reload of environment variable
-            envs.environment_variables[env_name] = lambda s=strategy: s
+            # Temporarily override the envs lookup so the router factory
+            # reads the monkeypatched value instead of the module-load-time
+            # default. Use monkeypatch.setitem so the original lambda is
+            # restored automatically at teardown.
+            monkeypatch.setitem(
+                envs.environment_variables,
+                env_name,
+                lambda s=strategy: s,
+            )

             # Test the select_experts method
             topk_weights, topk_ids = fused_moe.router.select_experts(
diff --git a/tests/kernels/moe/test_shared_fused_moe_routed_transform.py b/tests/kernels/moe/test_shared_fused_moe_routed_transform.py
index e431263d9b9a..366009dce99a 100644
--- a/tests/kernels/moe/test_shared_fused_moe_routed_transform.py
+++ b/tests/kernels/moe/test_shared_fused_moe_routed_transform.py
@@ -137,7 +137,7 @@ def test_routed_input_transform_inside_vs_outside(
     Method A (inside): SharedFusedMoE with routed_input_transform
     Method B (outside): Manually transform, then SharedFusedMoE without transform
     """
-    if current_platform.is_rocm() and use_rocm_aiter:
+    if current_platform.is_rocm():
         monkeypatch.setenv("VLLM_ROCM_USE_AITER", "1" if use_rocm_aiter else "0")
         monkeypatch.setenv("VLLM_ROCM_USE_AITER_MOE", "1" if use_rocm_aiter else "0")
         from vllm._aiter_ops import rocm_aiter_ops
diff --git a/vllm/distributed/parallel_state.py b/vllm/distributed/parallel_state.py
index 04187b34ec7a..dbe673b331ce 100644
--- a/vllm/distributed/parallel_state.py
+++ b/vllm/distributed/parallel_state.py
@@ -1905,6 +1905,17 @@ def destroy_distributed_environment():
 def cleanup_dist_env_and_memory(shutdown_ray: bool = False):
     # Reset environment variable cache
     envs.disable_envs_cache()
+
+    # Reset rocm_aiter_ops class variables to match current os.environ.
+    # These are class-level attributes that persist across tests and are
+    # NOT restored by monkeypatch (which only restores os.environ).
+    from vllm.platforms import current_platform
+
+    if current_platform.is_rocm():
+        from vllm._aiter_ops import rocm_aiter_ops
+
+        rocm_aiter_ops.refresh_env_variables()
+
     # Ensure all objects are not frozen before cleanup
     gc.unfreeze()

PATCH

echo "Patch applied successfully."
