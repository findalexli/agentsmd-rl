#!/usr/bin/env bash
set -euo pipefail

FILE="/workspace/transformers/src/transformers/configuration_utils.py"

# Idempotency: check if already patched
if grep -q 'if "model_type" in kwargs and config_dict\["model_type"\] != kwargs\["model_type"\]' "$FILE" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git -C /workspace/transformers apply - <<'PATCH'
diff --git a/src/transformers/configuration_utils.py b/src/transformers/configuration_utils.py
index afcae7ddd75c..9e28b2287e81 100755
--- a/src/transformers/configuration_utils.py
+++ b/src/transformers/configuration_utils.py
@@ -760,6 +760,15 @@ def _get_config_dict(
         if "model_type" not in config_dict and is_timm_config_dict(config_dict):
             config_dict["model_type"] = "timm_wrapper"

+        # Some checkpoints may contain the wrong model_type in the config file.
+        # Allow the user to override it but warn them that it might not work.
+        if "model_type" in kwargs and config_dict["model_type"] != kwargs["model_type"]:
+            logger.warning(
+                f"{configuration_file} has 'model_type={config_dict['model_type']}' but you overrode "
+                f"it with 'model_type={kwargs['model_type']}'. This may lead to unexpected behavior."
+            )
+            config_dict["model_type"] = kwargs["model_type"]
+
         return config_dict, kwargs

     @classmethod

PATCH

echo "Patch applied successfully."
