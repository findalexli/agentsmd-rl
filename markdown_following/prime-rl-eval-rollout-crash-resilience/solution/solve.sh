#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Idempotency check: if get_logger is already imported in vf_utils, patch is applied
if grep -q 'from prime_rl.utils.logger import InterceptHandler, ProgressTracker, get_logger' src/prime_rl/orchestrator/vf_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/orchestrator/eval_utils.py b/src/prime_rl/orchestrator/eval_utils.py
index 5dee7f3aff..8252fdf336 100644
--- a/src/prime_rl/orchestrator/eval_utils.py
+++ b/src/prime_rl/orchestrator/eval_utils.py
@@ -114,6 +114,10 @@ async def evaluate_env(
     )
     eval_time = time.perf_counter() - eval_start_time

+    if not outputs:
+        logger.warning(f"All rollouts failed for {env_name}, skipping metrics")
+        return
+
     rows = []
     for output in outputs:
         rows.append(
diff --git a/src/prime_rl/orchestrator/vf_utils.py b/src/prime_rl/orchestrator/vf_utils.py
index 6acfbee23e..0d0bb41d8d 100644
--- a/src/prime_rl/orchestrator/vf_utils.py
+++ b/src/prime_rl/orchestrator/vf_utils.py
@@ -10,7 +10,7 @@
 from verifiers.utils.worker_utils import get_free_port_pair
 from verifiers.workers import ZMQEnvClient, ZMQEnvServer

-from prime_rl.utils.logger import InterceptHandler, ProgressTracker
+from prime_rl.utils.logger import InterceptHandler, ProgressTracker, get_logger

 DEFAULT_RETRIES = 0
 REQUIRED_STATE_COLUMNS = ["trajectory", "sampling_args"]
@@ -163,29 +163,32 @@ async def get_client() -> vf.ClientConfig:
     total_rollouts = len(examples) * rollouts_per_example
     pbar = ProgressTracker(total=total_rollouts, desc=pbar_description)

-    async def run_group_with_progress(example):
-        client = await get_client()
-        result = await run_group(
-            env=env,
-            client=client,
-            model_name=model_name,
-            example=example,
-            rollouts_per_example=rollouts_per_example,
-            max_retries=max_retries,
-            state_columns=state_columns,
-            sampling_args=sampling_args,
-        )
-        pbar.update(rollouts_per_example)
-        return result
+    async def run_group_with_progress(example) -> list[vf.RolloutOutput] | None:
+        try:
+            client = await get_client()
+            result = await run_group(
+                env=env,
+                client=client,
+                model_name=model_name,
+                example=example,
+                rollouts_per_example=rollouts_per_example,
+                max_retries=max_retries,
+                state_columns=state_columns,
+                sampling_args=sampling_args,
+            )
+            pbar.update(rollouts_per_example)
+            return result
+        except Exception as e:
+            get_logger().warning(f"Group failed: {e}")
+            pbar.update(rollouts_per_example)
+            return None

     try:
-        group_outputs_list: list[list[vf.RolloutOutput]] = await asyncio.gather(
-            *[run_group_with_progress(example) for example in examples]
-        )
+        group_outputs_list = await asyncio.gather(*[run_group_with_progress(example) for example in examples])
     finally:
         pbar.close()

-    return [output for group_outputs in group_outputs_list for output in group_outputs]
+    return [output for group_outputs in group_outputs_list if group_outputs is not None for output in group_outputs]


 async def evaluate(

PATCH

echo "Patch applied successfully."
