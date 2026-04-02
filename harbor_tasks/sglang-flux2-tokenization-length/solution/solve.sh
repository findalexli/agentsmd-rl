#!/usr/bin/env bash
set -euo pipefail
cd /workspace/sglang

if grep -q 'max_length = 512' python/sglang/multimodal_gen/configs/pipeline_configs/flux.py 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py b/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py
index 71d0c0128372..d5f162cc7273 100644
--- a/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py
+++ b/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py
@@ -437,6 +437,17 @@ class Flux2PipelineConfig(FluxPipelineConfig):
         default_factory=lambda: (flux2_postprocess_text,)
     )
     vae_config: VAEConfig = field(default_factory=Flux2VAEConfig)
+    text_encoder_extra_args: list[dict] = field(
+        default_factory=lambda: [
+            dict(
+                max_length=512,
+                padding="max_length",
+                truncation=True,
+                return_overflowing_tokens=False,
+                return_length=False,
+            )
+        ]
+    )
 
     def tokenize_prompt(self, prompts: list[str], tokenizer, tok_kwargs) -> dict:
         # flatten to 1-d list
@@ -681,7 +692,9 @@ class Flux2KleinPipelineConfig(Flux2PipelineConfig):
         texts = [_apply_chat_template(prompt) for prompt in prompts]
 
         tok_kwargs = dict(tok_kwargs or {})
-        max_length = tok_kwargs.pop("max_length", 512)
+        tok_kwargs.pop("max_length", None)
+        # Flux2 Klein uses max_length 512.
+        max_length = 512
         padding = tok_kwargs.pop("padding", "max_length")
         truncation = tok_kwargs.pop("truncation", True)
         return_tensors = tok_kwargs.pop("return_tensors", "pt")

PATCH
