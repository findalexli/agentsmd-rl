#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotency: check if the fix is already applied
# The fix moves vlms_require_bfloat16 from ModelConfig to TrainerConfig,
# so after the fix, TrainerConfig has self.model.name instead of self.name
if grep -q 'self\.model\.name.*self\.model\.optimization_dtype' src/prime_rl/configs/trainer.py 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/configs/trainer.py b/src/prime_rl/configs/trainer.py
index 914bc054f2..d1fd1497f4 100644
--- a/src/prime_rl/configs/trainer.py
+++ b/src/prime_rl/configs/trainer.py
@@ -299,14 +299,6 @@ def trust_remote_code_only_with_hf(self):
                 raise ValueError("Trust remote code is only supported with the HF implementation or auto mode.")
         return self

-    @model_validator(mode="after")
-    def vlms_require_bfloat16(self):
-        if is_vlm_model(self.name) and (self.optimization_dtype != "bfloat16" or self.reduce_dtype != "bfloat16"):
-            raise ValueError(
-                "VLM models must use optimization_dtype='bfloat16' and reduce_dtype='bfloat16' to match vLLM inference."
-            )
-        return self
-
     @model_validator(mode="after")
     def cp_only_with_flash_attn(self):
         if self.cp > 1 and self.attn not in ["flash_attention_2", "flash_attention_3"]:
@@ -720,6 +712,16 @@ class TrainerConfig(BaseConfig):
         ),
     ] = 1

+    @model_validator(mode="after")
+    def vlms_require_bfloat16(self):
+        if is_vlm_model(self.model.name) and (
+            self.model.optimization_dtype != "bfloat16" or self.model.reduce_dtype != "bfloat16"
+        ):
+            raise ValueError(
+                "VLM models must use optimization_dtype='bfloat16' and reduce_dtype='bfloat16' to match vLLM inference."
+            )
+        return self
+
     @model_validator(mode="after")
     def auto_setup_bench(self):
         if self.bench is not None:

PATCH

echo "Patch applied successfully."
