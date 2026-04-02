#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotency check: if enable_metrics is already in the server args kwargs, patch is applied
if grep -q '"enable_metrics": True' slime/backends/sglang_utils/sglang_engine.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/backends/sglang_utils/sglang_engine.py b/slime/backends/sglang_utils/sglang_engine.py
index 0c3430a54..664d75834 100644
--- a/slime/backends/sglang_utils/sglang_engine.py
+++ b/slime/backends/sglang_utils/sglang_engine.py
@@ -535,11 +535,14 @@ def _compute_server_args(
         "skip_server_warmup": True,
         # always enable draft weights cpu backup so that we run training without mtp weights.
         "enable_draft_weights_cpu_backup": True,
+        # Always enable Prometheus metrics so the /engine_metrics endpoint is
+        # available for W&B scraping (regardless of --sglang-enable-metrics).
+        "enable_metrics": True,
     }

     if worker_type == "prefill":
         kwargs["disaggregation_mode"] = "prefill"
-        kwargs["load_balance_method"] = "round_robin"
+        kwargs["load_balance_method"] = "follow_bootstrap_room"
         assert (
             disaggregation_bootstrap_port is not None
         ), "disaggregation_bootstrap_port must be set for prefill worker"
@@ -603,5 +606,6 @@ def _compute_server_args(
     "dist_init_addr",
     "skip_server_warmup",
     "enable_draft_weights_cpu_backup",
+    "enable_metrics",
     "mem_fraction_static",
 ]
diff --git a/slime/ray/rollout.py b/slime/ray/rollout.py
index c422db53a..c8d2dc977 100644
--- a/slime/ray/rollout.py
+++ b/slime/ray/rollout.py
@@ -404,8 +404,6 @@ def _get_metrics_router_addr(self) -> str | None:
         Note: the ``use_slime_router`` path does not expose ``/engine_metrics``;
         metrics forwarding to W&B requires the sglang_router gateway.
         """
-        if not getattr(self.args, "sglang_enable_metrics", False):
-            return None
         if getattr(self.args, "use_slime_router", False):
             logger.warning(
                 "SGLang metrics forwarding to W&B is not supported with --use-slime-router. "
diff --git a/slime/rollout/sglang_rollout.py b/slime/rollout/sglang_rollout.py
index 7471e2580..e8f73d137 100644
--- a/slime/rollout/sglang_rollout.py
+++ b/slime/rollout/sglang_rollout.py
@@ -5,7 +5,6 @@
 import uuid
 from argparse import Namespace
 from collections.abc import Callable
-from contextlib import contextmanager
 from typing import Any

 import numpy as np
@@ -85,24 +84,8 @@ def __init__(self, args: Namespace) -> None:
             sampling_seed_base = args.rollout_seed
             self.group_sampling_seeds = [sampling_seed_base + i for i in range(args.n_samples_per_prompt)]

-        # dp rank balancing
-        self.dp_counts = [0] * (args.sglang_dp_size or 1)
-        self.dp_rank = 0
-
         self.reset()

-    @contextmanager
-    def dp_rank_context(self):
-        candidates = [i for i, count in enumerate(self.dp_counts) if count == min(self.dp_counts)]
-        dp_rank = int(np.random.choice(candidates))
-        self.dp_counts[dp_rank] += 1
-        self.dp_rank = dp_rank
-        try:
-            yield dp_rank
-        finally:
-            self.dp_counts[dp_rank] -= 1
-            assert self.dp_counts[dp_rank] >= 0
-
     def reset(self) -> None:
         self.remaining_batch_size = 0
         self.pendings = set()
@@ -253,19 +236,18 @@ async def generate_and_rm(
             sample.status = Sample.Status.ABORTED
             return sample

-        with state.dp_rank_context() as _:
-            # Check sample.generate_function_path for per-sample custom_generate_function_path (e.g., from eval dataset config)
-            custom_func_path = getattr(sample, "generate_function_path", None) or args.custom_generate_function_path
-
-            if custom_func_path is not None:
-                custom_generate_func = load_function(custom_func_path)
-                # if signature has evaluation, pass evaluation
-                if "evaluation" in inspect.signature(custom_generate_func).parameters:
-                    sample = await custom_generate_func(args, sample, sampling_params, evaluation=evaluation)
-                else:
-                    sample = await custom_generate_func(args, sample, sampling_params)
+        # Check sample.generate_function_path for per-sample custom_generate_function_path (e.g., from eval dataset config)
+        custom_func_path = getattr(sample, "generate_function_path", None) or args.custom_generate_function_path
+
+        if custom_func_path is not None:
+            custom_generate_func = load_function(custom_func_path)
+            # if signature has evaluation, pass evaluation
+            if "evaluation" in inspect.signature(custom_generate_func).parameters:
+                sample = await custom_generate_func(args, sample, sampling_params, evaluation=evaluation)
             else:
-                sample = await generate(args, sample, sampling_params)
+                sample = await custom_generate_func(args, sample, sampling_params)
+        else:
+            sample = await generate(args, sample, sampling_params)

     # for the rm that need the whole group, we will not do the rm here
     if args.group_rm:
diff --git a/slime/utils/wandb_utils.py b/slime/utils/wandb_utils.py
index bb491d1b0..6e8bf085e 100644
--- a/slime/utils/wandb_utils.py
+++ b/slime/utils/wandb_utils.py
@@ -116,7 +116,7 @@ def init_wandb_secondary(args, router_addr=None):
             x_update_finish_state=False,
         )

-    if getattr(args, "sglang_enable_metrics", False) and router_addr is not None:
+    if router_addr is not None:
         logger.info(f"Forward SGLang metrics at {router_addr} to WandB.")
         settings_kwargs |= dict(
             x_stats_open_metrics_endpoints={

PATCH

echo "Patch applied successfully."
