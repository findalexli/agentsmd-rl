#!/usr/bin/env bash
set -euo pipefail
cd /workspace/prime-rl

# Idempotency: check if already applied
if grep -q "log_eval_samples" src/prime_rl/utils/monitor/base.py 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/orchestrator/eval_utils.py b/src/prime_rl/orchestrator/eval_utils.py
index 8252fdf336..28b890f2c9 100644
--- a/src/prime_rl/orchestrator/eval_utils.py
+++ b/src/prime_rl/orchestrator/eval_utils.py
@@ -175,3 +175,4 @@ async def evaluate_env(
     eval_metrics.update({"progress/ckpt_step": ckpt_step, "step": step})
     monitor = get_monitor()
     monitor.log(eval_metrics, step=step)
+    monitor.log_eval_samples(outputs, env_name=env_name, step=step)
diff --git a/src/prime_rl/utils/monitor/base.py b/src/prime_rl/utils/monitor/base.py
index 2e72971e15..9dd3648f76 100644
--- a/src/prime_rl/utils/monitor/base.py
+++ b/src/prime_rl/utils/monitor/base.py
@@ -19,6 +19,10 @@ def log(self, metrics: dict[str, Any], step: int) -> None:
     def log_samples(self, rollouts: list[vf.RolloutOutput], step: int) -> None:
         pass

+    @abstractmethod
+    def log_eval_samples(self, rollouts: list[vf.RolloutOutput], env_name: str, step: int) -> None:
+        pass
+
     @abstractmethod
     def log_final_samples(self) -> None:
         pass
@@ -48,6 +52,9 @@ def log(self, metrics: dict[str, Any], step: int) -> None:
     def log_samples(self, rollouts: list[vf.RolloutOutput], step: int) -> None:
         pass

+    def log_eval_samples(self, rollouts: list[vf.RolloutOutput], env_name: str, step: int) -> None:
+        pass
+
     def log_final_samples(self) -> None:
         pass

diff --git a/src/prime_rl/utils/monitor/multi.py b/src/prime_rl/utils/monitor/multi.py
index a9dd1cf3a2..9761917b6b 100644
--- a/src/prime_rl/utils/monitor/multi.py
+++ b/src/prime_rl/utils/monitor/multi.py
@@ -33,6 +33,13 @@ def log_samples(self, rollouts: list[vf.RolloutOutput], step: int) -> None:
             except Exception as e:
                 self.logger.warning(f"Failed to log samples to {monitor.__class__.__name__}: {e}")

+    def log_eval_samples(self, rollouts: list[vf.RolloutOutput], env_name: str, step: int) -> None:
+        for monitor in self.monitors:
+            try:
+                monitor.log_eval_samples(rollouts=rollouts, env_name=env_name, step=step)
+            except Exception as e:
+                self.logger.warning(f"Failed to log eval samples to {monitor.__class__.__name__}: {e}")
+
     def log_final_samples(self) -> None:
         for monitor in self.monitors:
             try:
diff --git a/src/prime_rl/utils/monitor/prime.py b/src/prime_rl/utils/monitor/prime.py
index ab759f50b8..40567af671 100644
--- a/src/prime_rl/utils/monitor/prime.py
+++ b/src/prime_rl/utils/monitor/prime.py
@@ -446,6 +446,9 @@ async def _confirm_samples_upload(self, step: int, s3_key: str, max_retries: int
                 await asyncio.sleep(delay)
         return False

+    def log_eval_samples(self, rollouts: list[vf.RolloutOutput], env_name: str, step: int) -> None:
+        pass
+
     def log_final_samples(self) -> None:
         """Log final samples (no-op - samples are logged per-step only)."""
         pass
diff --git a/src/prime_rl/utils/monitor/wandb.py b/src/prime_rl/utils/monitor/wandb.py
index 8707d8a046..cba0147d04 100644
--- a/src/prime_rl/utils/monitor/wandb.py
+++ b/src/prime_rl/utils/monitor/wandb.py
@@ -102,6 +102,11 @@ def init_wandb(max_retries: int):
                 )
                 self.tokenizer = tokenizer
                 self.samples = []
+                self.eval_samples_cols = ["step", "env", "task", "example_id", "completion", "reward"]
+                self.eval_samples_table = wandb.Table(
+                    columns=self.eval_samples_cols,
+                    log_mode="INCREMENTAL",
+                )

     def _maybe_overwrite_wandb_command(self) -> None:
         """Overwrites sys.argv with the start command if it is set in the environment variables."""
@@ -165,6 +170,34 @@ def log_samples(self, rollouts: list[vf.RolloutOutput], step: int) -> None:
         self.last_log_samples_step = step
         self.logger.debug(f"Logged samples at step {step} to W&B table in {time.perf_counter() - start_time:.2f}s")

+    def log_eval_samples(self, rollouts: list[vf.RolloutOutput], env_name: str, step: int) -> None:
+        """Logs eval rollouts to a separate W&B table."""
+        if not self.is_master:
+            return
+        if (
+            not self.config
+            or not isinstance(self.config, WandbWithExtrasConfig)
+            or not self.config.log_extras
+            or not self.config.log_extras.samples
+        ):
+            return
+
+        for rollout in rollouts:
+            completion = rollout.get("completion", "")
+            if not completion:
+                continue
+            sample = {
+                "step": step,
+                "env": env_name,
+                "task": rollout.get("task"),
+                "example_id": rollout["example_id"],
+                "completion": completion,
+                "reward": rollout["reward"],
+            }
+            self.eval_samples_table.add_data(*sample.values())
+
+        wandb.log({"eval/samples": self.eval_samples_table, "step": step})
+
     def log_final_samples(self) -> None:
         """Log final samples to W&B table."""
         if not self.is_master:

PATCH
