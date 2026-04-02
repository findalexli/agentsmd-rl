#!/usr/bin/env bash
set -euo pipefail
cd /workspace/slime

if grep -q "reinit_wandb_primary_with_open_metrics" slime/utils/wandb_utils.py 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/ray/rollout.py b/slime/ray/rollout.py
index b3f85508a..a584e7e29 100644
--- a/slime/ray/rollout.py
+++ b/slime/ray/rollout.py
@@ -378,10 +378,7 @@ def __init__(self, args, pg):
             init_http_client(args)
             self.servers = start_rollout_servers(args, pg)

-        # Initialize W&B secondary *after* servers are launched so the router
-        # address is available for scraping SGLang Prometheus metrics.
-        router_addr = self._get_metrics_router_addr()
-        init_tracking(args, primary=False, router_addr=router_addr)
+        init_tracking(args, primary=False)
         self.rollout_engine_lock = Lock.options(num_cpus=1, num_gpus=0).remote()
         self.rollout_id = -1

@@ -416,6 +413,10 @@ def _get_metrics_router_addr(self) -> str | None:
             return None
         return f"http://{srv.router_ip}:{srv.router_port}"

+    def get_metrics_router_addr(self) -> str | None:
+        """Public wrapper for remote calls from the driver process."""
+        return self._get_metrics_router_addr()
+
     def _try_ci_fault_injection(self):
         """Try to inject fault during generate (when health monitor is running)."""
         if not self._ci_fault_injection_pending:
diff --git a/slime/utils/logging_utils.py b/slime/utils/logging_utils.py
index 1fc3d94b2..11348a407 100644
--- a/slime/utils/logging_utils.py
+++ b/slime/utils/logging_utils.py
@@ -31,6 +31,10 @@ def init_tracking(args, primary: bool = True, **kwargs):
         wandb_utils.init_wandb_secondary(args, **kwargs)


+def update_tracking_open_metrics(args, router_addr):
+    wandb_utils.reinit_wandb_primary_with_open_metrics(args, router_addr)
+
+
 def finish_tracking(args):
     if not args.use_wandb:
         return
diff --git a/slime/utils/wandb_utils.py b/slime/utils/wandb_utils.py
index 6e8bf085e..cd5302049 100644
--- a/slime/utils/wandb_utils.py
+++ b/slime/utils/wandb_utils.py
@@ -79,6 +79,56 @@ def init_wandb_primary(args):
     args.wandb_run_id = wandb.run.id


+def reinit_wandb_primary_with_open_metrics(args, router_addr):
+    """Re-initialize the primary W&B run with open metrics endpoints.
+
+    The primary wandb init happens before rollout servers start (to obtain
+    ``wandb_run_id`` for secondary processes).  This function is called
+    *after* servers are up so the router address is available for scraping
+    SGLang Prometheus metrics via the primary process's stats monitor.
+    """
+    if not args.use_wandb or _is_offline_mode(args):
+        return
+    if router_addr is None:
+        return
+
+    import sglang_router
+
+    if "slime" not in sglang_router.__version__:
+        logger.warning(
+            "Only customized sglang_router from https://github.com/zhuzilin/sgl-router supports uploading metrics."
+        )
+        return
+
+    logger.info(f"Re-initializing primary W&B with SGLang metrics at {router_addr}.")
+
+    wandb.finish()
+
+    init_kwargs = {
+        "id": args.wandb_run_id,
+        "entity": args.wandb_team,
+        "project": args.wandb_project,
+        "resume": "allow",
+        "reinit": True,
+        "settings": wandb.Settings(
+            mode="shared",
+            x_primary=True,
+            x_stats_open_metrics_endpoints={
+                "sgl_engine": f"{router_addr}/engine_metrics",
+            },
+            x_stats_open_metrics_filters={
+                "sgl_engine.*": {},
+            },
+        ),
+    }
+
+    if args.wandb_dir:
+        init_kwargs["dir"] = args.wandb_dir
+
+    wandb.init(**init_kwargs)
+    _init_wandb_common()
+
+
 def _compute_config_for_logging(args):
     output = deepcopy(args.__dict__)

@@ -92,7 +142,7 @@ def _compute_config_for_logging(args):


 # https://docs.wandb.ai/guides/track/log/distributed-training/#track-all-processes-to-a-single-run
-def init_wandb_secondary(args, router_addr=None):
+def init_wandb_secondary(args):
     wandb_run_id = getattr(args, "wandb_run_id", None)
     if wandb_run_id is None:
         return
@@ -116,17 +166,6 @@ def init_wandb_secondary(args, router_addr=None):
             x_update_finish_state=False,
         )

-    if router_addr is not None:
-        logger.info(f"Forward SGLang metrics at {router_addr} to WandB.")
-        settings_kwargs |= dict(
-            x_stats_open_metrics_endpoints={
-                "sgl_engine": f"{router_addr}/engine_metrics",
-            },
-            x_stats_open_metrics_filters={
-                "sgl_engine.*": {},
-            },
-        )
-
     init_kwargs = {
         "id": wandb_run_id,
         "entity": args.wandb_team,
diff --git a/train.py b/train.py
index 71807a702..7bba9a367 100644
--- a/train.py
+++ b/train.py
@@ -2,7 +2,7 @@

 from slime.ray.placement_group import create_placement_groups, create_rollout_manager, create_training_models
 from slime.utils.arguments import parse_args
-from slime.utils.logging_utils import configure_logger, finish_tracking, init_tracking
+from slime.utils.logging_utils import configure_logger, finish_tracking, init_tracking, update_tracking_open_metrics
 from slime.utils.misc import should_run_periodic_action


@@ -16,6 +16,10 @@ def train(args):
     # need to initialize rollout manager first to calculate num_rollout
     rollout_manager, num_rollout_per_epoch = create_rollout_manager(args, pgs["rollout"])

+    # Update primary W&B with SGLang metrics endpoint now that servers are up.
+    router_addr = ray.get(rollout_manager.get_metrics_router_addr.remote())
+    update_tracking_open_metrics(args, router_addr)
+
     # create the actor and critic models
     actor_model, critic_model = create_training_models(args, pgs, rollout_manager)

diff --git a/train_async.py b/train_async.py
index 0325b204b..94cc29694 100644
--- a/train_async.py
+++ b/train_async.py
@@ -2,7 +2,7 @@

 from slime.ray.placement_group import create_placement_groups, create_rollout_manager, create_training_models
 from slime.utils.arguments import parse_args
-from slime.utils.logging_utils import configure_logger, finish_tracking, init_tracking
+from slime.utils.logging_utils import configure_logger, finish_tracking, init_tracking, update_tracking_open_metrics
 from slime.utils.misc import should_run_periodic_action


@@ -18,6 +18,10 @@ def train(args):
     # need to initialize rollout manager first to calculate num_rollout
     rollout_manager, num_rollout_per_epoch = create_rollout_manager(args, pgs["rollout"])

+    # Update primary W&B with SGLang metrics endpoint now that servers are up.
+    router_addr = ray.get(rollout_manager.get_metrics_router_addr.remote())
+    update_tracking_open_metrics(args, router_addr)
+
     # create the actor and critic models
     actor_model, critic_model = create_training_models(args, pgs, rollout_manager)

PATCH
