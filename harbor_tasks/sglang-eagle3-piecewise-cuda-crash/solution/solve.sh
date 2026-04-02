#!/usr/bin/env bash
set -euo pipefail
cd /workspace/sglang

FILE=python/sglang/srt/model_executor/model_runner.py

# Idempotent: skip if already applied
grep -q 'not hasattr(language_model.model, "layers")' "$FILE" && exit 0

git apply - <<'PATCH'
diff --git a/python/sglang/srt/model_executor/model_runner.py b/python/sglang/srt/model_executor/model_runner.py
index fc9afafac90b..fb5c5cff3200 100644
--- a/python/sglang/srt/model_executor/model_runner.py
+++ b/python/sglang/srt/model_executor/model_runner.py
@@ -2379,6 +2379,14 @@ def init_piecewise_cuda_graphs(self):
         # Collect attention layers and moe layers from the model
         self.model.model = resolve_language_model(self.model)
         language_model = getattr(self.model, "language_model", self.model)
+
+        # Some draft models (e.g. eagle3) don't have a standard 'layers' attribute
+        if not hasattr(language_model.model, "layers"):
+            logger.warning(
+                "Disable piecewise CUDA graph because the model does not have a 'layers' attribute"
+            )
+            return
+
         self.attention_layers = []
         self.moe_layers = []
         self.moe_fusions = []

PATCH
