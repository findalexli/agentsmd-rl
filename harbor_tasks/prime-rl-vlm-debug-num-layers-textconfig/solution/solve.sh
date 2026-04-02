#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Check if already applied
if grep -q 'target_config = getattr(model_config, "text_config", model_config)' src/prime_rl/trainer/model.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/trainer/model.py b/src/prime_rl/trainer/model.py
index d5206f7e2c..f1988583d6 100644
--- a/src/prime_rl/trainer/model.py
+++ b/src/prime_rl/trainer/model.py
@@ -249,11 +249,13 @@ def get_model(
     logger.debug(f"Loaded model config ({model_config.to_dict()})")

     if config.debug.num_layers is not None:
-        num_hidden_layers = min(config.debug.num_layers, model_config.num_hidden_layers)
+        # VLM configs nest num_hidden_layers under text_config
+        target_config = getattr(model_config, "text_config", model_config)
+        num_hidden_layers = min(config.debug.num_layers, target_config.num_hidden_layers)
         logger.warning(
-            f"Setting the number of layers to {config.debug.num_layers} in the model config. This means {model_config.num_hidden_layers - num_hidden_layers} layers will not be loaded."
+            f"Setting the number of layers to {config.debug.num_layers} in the model config. This means {target_config.num_hidden_layers - num_hidden_layers} layers will not be loaded."
         )
-        model_config.num_hidden_layers = num_hidden_layers
+        target_config.num_hidden_layers = num_hidden_layers

     # Determine the implementation to use
     custom_vlm_cls = get_custom_vlm_cls(model_config) if is_vlm else None

PATCH

echo "Patch applied successfully."
