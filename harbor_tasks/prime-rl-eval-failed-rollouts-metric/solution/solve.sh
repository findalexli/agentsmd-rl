#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Idempotency check: if failed_rollouts is already in eval metrics, patch is applied
if grep -q '"failed_rollouts": failed_rollouts' src/prime_rl/orchestrator/eval_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/orchestrator/eval_utils.py b/src/prime_rl/orchestrator/eval_utils.py
index 8252fdf336..848b972e0f 100644
--- a/src/prime_rl/orchestrator/eval_utils.py
+++ b/src/prime_rl/orchestrator/eval_utils.py
@@ -103,6 +103,7 @@ async def evaluate_env(
     logger = get_logger()
     logger.info(f"Evaluating {env_name} ({num_examples=}, {rollouts_per_example=})")
     eval_start_time = time.perf_counter()
+    total_inputs = len(env._get_eval_inputs(num_examples, rollouts_per_example))
     outputs = await evaluate(
         env=env,
         model_name=model_name,
@@ -113,9 +114,15 @@ async def evaluate_env(
         max_retries=max_retries,
     )
     eval_time = time.perf_counter() - eval_start_time
+    failed_rollouts = total_inputs - len(outputs)

     if not outputs:
-        logger.warning(f"All rollouts failed for {env_name}, skipping metrics")
+        logger.warning(f"All rollouts failed for {env_name} ({failed_rollouts} failed), skipping metrics")
+        monitor = get_monitor()
+        monitor.log(
+            {f"eval/{env_name}/failed_rollouts": failed_rollouts, "progress/ckpt_step": ckpt_step, "step": step},
+            step=step,
+        )
         return

     rows = []
@@ -166,6 +173,7 @@ async def evaluate_env(
         "completion_len/max": results_df.completion_len.max().item(),
         "completion_len/min": results_df.completion_len.min().item(),
         "is_truncated/mean": results_df.is_truncated.mean().item(),
+        "failed_rollouts": failed_rollouts,
         "time": eval_time,
     }
     if could_be_binary:
diff --git a/src/prime_rl/orchestrator/vf_utils.py b/src/prime_rl/orchestrator/vf_utils.py
index 3e850d8334..7c20deb171 100644
--- a/src/prime_rl/orchestrator/vf_utils.py
+++ b/src/prime_rl/orchestrator/vf_utils.py
@@ -207,6 +207,10 @@ async def run_group_with_progress(example) -> list[vf.RolloutOutput] | None:
     finally:
         pbar.close()

+    failed_groups = sum(1 for g in group_outputs_list if g is None)
+    if failed_groups:
+        get_logger().warning(f"{failed_groups}/{len(group_outputs_list)} groups failed")
+
     return [output for group_outputs in group_outputs_list if group_outputs is not None for output in group_outputs]


@@ -229,7 +233,7 @@ async def evaluate(

     """
     inputs = env._get_eval_inputs(num_examples, rollouts_per_example)
-    outputs = await generate(
+    return await generate(
         env=env,
         clients=clients,
         get_client=get_client,
@@ -244,7 +248,6 @@ async def evaluate(
         max_retries=max_retries,
         state_columns=state_columns,
     )
-    return outputs


 # TODO: remove once usage is tracked by verifiers

PATCH

echo "Patch applied successfully."
