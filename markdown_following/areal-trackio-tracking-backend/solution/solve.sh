#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotent: skip if already applied
if grep -q 'class TrackioConfig' areal/api/cli_args.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/api/cli_args.py b/areal/api/cli_args.py
index 010509522..f9f7828cc 100644
--- a/areal/api/cli_args.py
+++ b/areal/api/cli_args.py
@@ -1902,6 +1902,36 @@ class TensorBoardConfig:
     path: str | None = None


+@dataclass
+class TrackioConfig:
+    """Configuration for Trackio experiment tracking (Hugging Face).
+
+    Trackio is a lightweight, local-first experiment tracking library
+    with a wandb-compatible API. Dashboards can be viewed locally or
+    deployed to Hugging Face Spaces.
+
+    See: https://github.com/gradio-app/trackio
+    """
+
+    mode: str = "disabled"
+    """Tracking mode. One of "disabled", "online", or "local"."""
+    project: str | None = None
+    """Project name. Defaults to experiment_name if not set."""
+    name: str | None = None
+    """Run name. Defaults to trial_name if not set."""
+    space_id: str | None = None
+    """HF Space ID for remote dashboard deployment (e.g. "user/my-space").
+    When set, metrics are also pushed to the specified Hugging Face Space."""
+
+    def __post_init__(self):
+        """Validate Trackio configuration."""
+        valid_modes = {"disabled", "online", "local"}
+        if self.mode not in valid_modes:
+            raise ValueError(
+                f"Invalid trackio mode: '{self.mode}'. Must be one of {valid_modes}."
+            )
+
+
 @dataclass
 class StatsLoggerConfig:
     """Configuration for experiment statistics logging and tracking services."""
@@ -1921,6 +1951,10 @@ class StatsLoggerConfig:
         default_factory=TensorBoardConfig,
         metadata={"help": "TensorBoard configuration. Only 'path' field required."},
     )
+    trackio: TrackioConfig = field(
+        default_factory=TrackioConfig,
+        metadata={"help": "Trackio configuration (Hugging Face experiment tracking)."},
+    )


 @dataclass
diff --git a/areal/utils/logging.py b/areal/utils/logging.py
index 52a9cbf21..35c8bb8e5 100644
--- a/areal/utils/logging.py
+++ b/areal/utils/logging.py
@@ -414,7 +414,7 @@ def setup_file_logging(


 def log_swanlab_wandb_tensorboard(data, step=None, summary_writer=None):
-    # Logs data to SwanLab、 wandb、 TensorBoard.
+    # Logs data to SwanLab, wandb, TensorBoard, and Trackio.

     global _LATEST_LOG_STEP
     if step is None:
@@ -435,6 +435,14 @@ def log_swanlab_wandb_tensorboard(data, step=None, summary_writer=None):

     wandb.log(data, step=step)

+    # trackio
+    try:
+        import trackio
+
+        trackio.log(data, step=step)
+    except (ModuleNotFoundError, ImportError):
+        pass
+
     # tensorboard
     if summary_writer is not None:
         for key, val in data.items():
diff --git a/areal/utils/stats_logger.py b/areal/utils/stats_logger.py
index d03db3745..54e695b50 100644
--- a/areal/utils/stats_logger.py
+++ b/areal/utils/stats_logger.py
@@ -5,6 +5,7 @@

 import swanlab
 import torch.distributed as dist
+import trackio
 import wandb
 from tensorboardX import SummaryWriter

@@ -90,6 +91,19 @@ def init(self):
             logdir=self.get_log_path(self.config),
             mode=swanlab_config.mode,
         )
+
+        # trackio init
+        self._trackio_enabled = False
+        trackio_config = self.config.trackio
+        if trackio_config.mode != "disabled":
+            trackio.init(
+                project=trackio_config.project or self.config.experiment_name,
+                name=trackio_config.name or self.config.trial_name,
+                config=exp_config_dict,
+                space_id=trackio_config.space_id,
+            )
+            self._trackio_enabled = True
+
         # tensorboard logging
         self.summary_writer = None
         if self.config.tensorboard.path is not None:
@@ -111,6 +125,8 @@ def close(self):
         )
         wandb.finish()
         swanlab.finish()
+        if getattr(self, "_trackio_enabled", False):
+            trackio.finish()
         if self.summary_writer is not None:
             self.summary_writer.close()

@@ -133,6 +149,8 @@ def commit(self, epoch: int, step: int, global_step: int, data: dict | list[dict
             self.print_stats(item)
             wandb.log(item, step=log_step + i)
             swanlab.log(item, step=log_step + i)
+            if getattr(self, "_trackio_enabled", False):
+                trackio.log(item, step=log_step + i)
             if self.summary_writer is not None:
                 for key, val in item.items():
                     self.summary_writer.add_scalar(f"{key}", val, log_step + i)
diff --git a/docs/generate_cli_docs.py b/docs/generate_cli_docs.py
index bee4d9fda..270d1f7b0 100644
--- a/docs/generate_cli_docs.py
+++ b/docs/generate_cli_docs.py
@@ -85,6 +85,7 @@ def categorize_dataclasses(
         "WandBConfig",
         "SwanlabConfig",
         "TensorBoardConfig",
+        "TrackioConfig",
         "SaverConfig",
         "EvaluatorConfig",
         "RecoverConfig",
diff --git a/pyproject.toml b/pyproject.toml
index 63fc6b168..426cfe2db 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -107,6 +107,7 @@ dependencies = [
     # Monitoring and logging
     "wandb",
     "tensorboardx",
+    "trackio",
     "colorama",
     "colorlog",
     "swanboard==0.1.9b1",

PATCH

echo "Patch applied successfully."
