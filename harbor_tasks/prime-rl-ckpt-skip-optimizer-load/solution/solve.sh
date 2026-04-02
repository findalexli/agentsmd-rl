#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotency: check if fix is already applied
if grep -q 'skip_optimizer' src/prime_rl/configs/trainer.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/configs/trainer.py b/src/prime_rl/configs/trainer.py
index db563bba48..385bdb0107 100644
--- a/src/prime_rl/configs/trainer.py
+++ b/src/prime_rl/configs/trainer.py
@@ -526,6 +526,13 @@ class CheckpointConfig(BaseConfig):
         ),
     ] = False

+    skip_optimizer: Annotated[
+        bool,
+        Field(
+            description="Whether to skip loading the optimizer state from checkpoint.",
+        ),
+    ] = False
+

 class DefaultLossConfig(BaseModel):
     """Config for the default loss."""
diff --git a/src/prime_rl/trainer/ckpt.py b/src/prime_rl/trainer/ckpt.py
index f2416c29f2..606ea47648 100644
--- a/src/prime_rl/trainer/ckpt.py
+++ b/src/prime_rl/trainer/ckpt.py
@@ -118,6 +118,7 @@ class CheckpointManager:

     def __init__(self, output_dir: Path, config: CheckpointConfig):
         self.config = config
+        self.skip_optimizer = config.skip_optimizer
         self.ckpt_dir = get_ckpt_dir(output_dir)
         self.logger = get_logger()
         self.world = get_world()
@@ -179,7 +180,7 @@ def load_from_path(
         start_time = time.perf_counter()

         # Load sharded state
-        app_state = AppState(model, optimizers, scheduler, progress)
+        app_state = AppState(model, optimizers if not self.skip_optimizer else [], scheduler, progress)
         state_dict = {"app": app_state}
         dcp_load(state_dict=state_dict, checkpoint_id=path)

PATCH

echo "Patch applied successfully."
