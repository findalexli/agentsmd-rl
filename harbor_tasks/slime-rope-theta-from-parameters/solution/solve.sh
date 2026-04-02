#!/usr/bin/env bash
set -euo pipefail
cd /workspace/slime

# Idempotent: skip if already applied
if grep -q 'rope_parameters' slime_plugins/mbridge/deepseek_v32.py; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime_plugins/mbridge/deepseek_v32.py b/slime_plugins/mbridge/deepseek_v32.py
index d3a4ee7977..d45fd40fe6 100644
--- a/slime_plugins/mbridge/deepseek_v32.py
+++ b/slime_plugins/mbridge/deepseek_v32.py
@@ -6,6 +6,15 @@

 @register_model("deepseek_v32")
 class DeepseekV32Bridge(DeepseekV3Bridge):
+
+    def __init__(self, hf_config, **kwargs):
+        # transformers 5.x stores rope_theta inside rope_parameters dict,
+        # but DeepseekV3Bridge._build_config() expects hf_config.rope_theta directly.
+        if not hasattr(hf_config, "rope_theta"):
+            rope_params = getattr(hf_config, "rope_parameters", None) or {}
+            hf_config.rope_theta = rope_params.get("rope_theta", 1000000)
+        super().__init__(hf_config, **kwargs)
+
     _DSA_ATTENTION_MAPPING = {
         "self_attention.wq_b.weight": ["model.layers.{layer_number}.self_attn.indexer.wq_b.weight"],
         "self_attention.wk.weight": ["model.layers.{layer_number}.self_attn.indexer.wk.weight"],

PATCH
