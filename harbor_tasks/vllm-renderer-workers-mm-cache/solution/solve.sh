#!/usr/bin/env bash
set -euo pipefail
cd /workspace/vllm

if grep -q "renderer_num_workers > 1" vllm/config/model.py 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/config/model.py b/vllm/config/model.py
index acb43a04b157..b8c601334a1d 100644
--- a/vllm/config/model.py
+++ b/vllm/config/model.py
@@ -647,6 +647,19 @@ class ModelConfig:
 
             self.multimodal_config = MultiModalConfig(**mm_config_kwargs)  # type: ignore[arg-type]
 
+            if (
+                self.renderer_num_workers > 1
+                and self.multimodal_config.mm_processor_cache_gb > 0
+            ):
+                raise ValueError(
+                    "Cannot use --renderer-num-workers > 1 with the "
+                    "multimodal processor cache enabled. The cache is "
+                    "not thread-safe and does not support concurrent "
+                    "renderer workers. Please set "
+                    "--renderer-num-workers 1 (the default), or "
+                    "disable the cache with --mm-processor-cache-gb 0."
+                )
+
         # Multimodal GGUF models must use original repo for mm processing
         if is_gguf(self.tokenizer) and self.is_multimodal_model:
             raise ValueError(

PATCH
