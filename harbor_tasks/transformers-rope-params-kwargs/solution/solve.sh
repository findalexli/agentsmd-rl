#!/usr/bin/env bash
set -euo pipefail
cd /workspace/transformers

# Check if patch is already applied by looking for the elif branch
if grep -q 'elif kwargs.get("rope_scaling") and kwargs.get("rope_theta")' src/transformers/configuration_utils.py; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/configuration_utils.py b/src/transformers/configuration_utils.py
index afcae7ddd75c..b84556efbb19 100755
--- a/src/transformers/configuration_utils.py
+++ b/src/transformers/configuration_utils.py
@@ -263,6 +263,12 @@ def __post_init__(self, **kwargs):
         # BC for rotary embeddings. We will pop out legacy keys from kwargs and rename to new format
         if hasattr(self, "rope_parameters"):
             kwargs = self.convert_rope_params_to_dict(**kwargs)
+        elif kwargs.get("rope_scaling") and kwargs.get("rope_theta"):
+            logger.warning(
+                f"{self.__class__.__name__} got `key=rope_scaling` in kwargs but hasn't set it as attribute. "
+                "For RoPE standardization you need to set `self.rope_parameters` in model's config. "
+            )
+            kwargs = self.convert_rope_params_to_dict(**kwargs)

         # Parameters for sequence generation saved in the config are popped instead of loading them.
         for parameter_name in GenerationConfig._get_default_generation_params().keys():
PATCH
