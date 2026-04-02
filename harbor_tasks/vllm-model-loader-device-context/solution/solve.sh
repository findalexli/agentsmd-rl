#!/usr/bin/env bash
set -euo pipefail

TARGET="/workspace/vllm/vllm/model_executor/model_loader/base_loader.py"

# Idempotency: check if already fixed (nested with statements instead of combined)
if grep -q 'with set_default_torch_dtype(model_config.dtype):' "$TARGET" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

cd /workspace/vllm

git apply - <<'PATCH'
diff --git a/vllm/model_executor/model_loader/base_loader.py b/vllm/model_executor/model_loader/base_loader.py
index f68405d05f87..d6c38664fde6 100644
--- a/vllm/model_executor/model_loader/base_loader.py
+++ b/vllm/model_executor/model_loader/base_loader.py
@@ -50,10 +50,14 @@ def load_model(
             device_config.device if load_config.device is None else load_config.device
         )
         target_device = torch.device(load_device)
-        with set_default_torch_dtype(model_config.dtype), target_device:
-            model = initialize_model(
-                vllm_config=vllm_config, model_config=model_config, prefix=prefix
-            )
+        with set_default_torch_dtype(model_config.dtype):
+            with target_device:
+                model = initialize_model(
+                    vllm_config=vllm_config,
+                    model_config=model_config,
+                    prefix=prefix,
+                )
+
             log_model_inspection(model)

             logger.debug("Loading weights on %s ...", load_device)

PATCH

echo "Patch applied successfully."
