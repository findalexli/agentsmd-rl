#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/workspace/slime"
cd "$REPO_ROOT"

# Idempotency check: if keyword args already present, patch was applied
if grep -q 'master_address=master_address' slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py b/slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py
index 7b5b7817f..6a7182e7b 100644
--- a/slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py
+++ b/slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py
@@ -278,11 +278,11 @@ def connect_rollout_engines_from_distributed(

     refs = [
         engine.init_weights_update_group.remote(
-            master_address,
-            master_port,
-            cumulative[i] + 1,
-            world_size,
-            group_name,
+            master_address=master_address,
+            master_port=master_port,
+            rank_offset=cumulative[i] + 1,
+            world_size=world_size,
+            group_name=group_name,
             backend="nccl",
         )
         for i, engine in enumerate(rollout_engines)
diff --git a/slime/ray/rollout.py b/slime/ray/rollout.py
index 727b581b9..b3f85508a 100644
--- a/slime/ray/rollout.py
+++ b/slime/ray/rollout.py
@@ -112,7 +112,8 @@ def start_engines(self, port_cursors: dict[int, int] | None = None) -> tuple[lis
             env_vars = {name: "1" for name in NOSET_VISIBLE_DEVICES_ENV_VARS_LIST} | {
                 key: os.environ.get(key, default_val)
                 for key, default_val in {
-                    "SGLANG_JIT_DEEPGEMM_PRECOMPILE": "false",
+                    "SGLANG_JIT_DEEPGEMM_PRECOMPILE": "true",
+                    "SGLANG_JIT_DEEPGEMM_FAST_WARMUP": "true",
                     "SGL_DISABLE_TP_MEMORY_INBALANCE_CHECK": "true",
                     "SGLANG_DISABLE_TP_MEMORY_INBALANCE_CHECK": "true",
                     "SGLANG_MEMORY_SAVER_CUDA_GRAPH": "true",

PATCH

echo "Patch applied successfully."
