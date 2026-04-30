#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotency: if patch already applied, exit early.
if grep -q 'def compute_eval_ckpt_step' src/prime_rl/orchestrator/eval_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prime_rl/orchestrator/eval_utils.py b/src/prime_rl/orchestrator/eval_utils.py
index 89ec477ff4..5dee7f3aff 100644
--- a/src/prime_rl/orchestrator/eval_utils.py
+++ b/src/prime_rl/orchestrator/eval_utils.py
@@ -13,6 +13,32 @@
 from prime_rl.utils.utils import capitalize


+def compute_eval_ckpt_step(
+    ckpt_step: int,
+    prev_ckpt_step: int,
+    last_eval_step: int,
+    interval: int,
+    eval_base_model: bool = True,
+) -> int | None:
+    """Determine which checkpoint step (if any) should trigger an eval.
+
+    Handles the case where ckpt_step jumps over interval boundaries by finding
+    the highest interval-aligned step in (prev_ckpt_step, ckpt_step].
+
+    Returns the interval step to eval at, or None if no eval should run.
+    """
+    if ckpt_step <= prev_ckpt_step:
+        return None
+    highest_interval_step = (ckpt_step // interval) * interval
+    if highest_interval_step > prev_ckpt_step and highest_interval_step > last_eval_step:
+        if highest_interval_step == 0:
+            if ckpt_step == 0 and eval_base_model:
+                return 0
+        else:
+            return highest_interval_step
+    return None
+
+
 def get_eval_sampling_args(sampling_config: EvalSamplingConfig) -> dict[str, Any]:
     """Get sampling args for evaluation."""
     # Initialize sampling args
diff --git a/src/prime_rl/orchestrator/orchestrator.py b/src/prime_rl/orchestrator/orchestrator.py
index 0b6bce59bd..92be3ace56 100644
--- a/src/prime_rl/orchestrator/orchestrator.py
+++ b/src/prime_rl/orchestrator/orchestrator.py
@@ -7,7 +7,7 @@
 import tomli_w

 from prime_rl.orchestrator.advantage import compute_advantages
-from prime_rl.orchestrator.eval_utils import get_eval_sampling_args
+from prime_rl.orchestrator.eval_utils import compute_eval_ckpt_step, get_eval_sampling_args
 from prime_rl.orchestrator.event_loop_lag import EventLoopLagMonitor
 from prime_rl.orchestrator.patches import monkey_patch_chat_completion_logprobs, monkey_patch_oai_iterable_types
 from prime_rl.orchestrator.trajectories import build_vlm_image_cache, interleave_rollout
@@ -309,6 +309,8 @@ async def orchestrate(config: OrchestratorConfig):

     # Track last online eval checkpoint step for this process
     last_eval_step = -1
+    # Track previous ckpt_step to detect when ckpt_step jumps over eval interval boundaries
+    prev_ckpt_step = -1

     # Reset weights to base model if starting from scratch
     progress = Progress()
@@ -318,8 +320,12 @@ async def orchestrate(config: OrchestratorConfig):
         logger.info(f"Resuming training from checkpoint step {checkpoint_step}")
         scheduler.ckpt_step = progress.step  # Always resume from the latest checkpoint
         if config.eval and config.eval.skip_eval_on_resume:
+            prev_ckpt_step = scheduler.ckpt_step
             last_eval_step = scheduler.ckpt_step
             logger.info(f"Skipping online eval on resume (ckpt_step={scheduler.ckpt_step})")
+        else:
+            # Allow eval at resumed step by setting prev_ckpt_step one behind
+            prev_ckpt_step = scheduler.ckpt_step - 1

         # In NCCL mode, skip existence check - weights are broadcasted, not stored on disk
         check_exists = config.weight_broadcast.type != "nccl"
@@ -376,16 +382,25 @@ async def orchestrate(config: OrchestratorConfig):
         logger.info(f"Starting orchestrator step {progress.step}")
         step_start_time = time.perf_counter()

-        # Run evals BEFORE training (blocking, in subprocess to isolate event loop)
-        # This ensures weights don't change during eval and eval doesn't cause event loop lag
-        if (
-            config.eval
-            and ckpt_step % config.eval.interval == 0
-            and ckpt_step > last_eval_step
-            and ((ckpt_step == 0 and config.eval.eval_base_model) or ckpt_step > 0)
-        ):
+        # Run evals BEFORE training (blocking). Weight updates are paused via
+        # scheduler.checkpoint_ready during eval to ensure consistent weights.
+        # Use range check to handle ckpt_step jumping over interval boundaries.
+        eval_ckpt_step = None
+        if config.eval:
+            eval_ckpt_step = compute_eval_ckpt_step(
+                ckpt_step=ckpt_step,
+                prev_ckpt_step=prev_ckpt_step,
+                last_eval_step=last_eval_step,
+                interval=config.eval.interval,
+                eval_base_model=config.eval.eval_base_model,
+            )
+
+        if eval_ckpt_step is not None:
             last_eval_step = ckpt_step
-            logger.info(f"Running evals for checkpoint step {ckpt_step}")
+            if eval_ckpt_step != ckpt_step:
+                logger.info(f"Running evals for interval step {eval_ckpt_step} (current ckpt_step={ckpt_step})")
+            else:
+                logger.info(f"Running evals for checkpoint step {ckpt_step}")

             # Pause weight updates and re-scheduling of training rollouts during eval
             # to avoid evaluating across different checkpoints and avoid congestion
@@ -417,6 +432,9 @@ async def orchestrate(config: OrchestratorConfig):
             # Resume weight updates
             scheduler.checkpoint_ready.set()

+        # Update prev_ckpt_step for next iteration
+        prev_ckpt_step = ckpt_step
+
         # Schedule generating the training batch
         temperature = compute_temperature(progress.step, config.sampling, config.max_steps)
         sampling_args = get_sampling_args(config.sampling, temperature=temperature)
PATCH

echo "Patch applied."
