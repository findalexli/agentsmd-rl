#!/usr/bin/env bash
set -euo pipefail

REPO="/workspace/transformers"
cd "$REPO"

# Check if already applied (look for h2ovl_chat in the set, a distinctive addition)
if grep -q '"h2ovl_chat"' src/transformers/models/auto/tokenization_auto.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/models/auto/tokenization_auto.py b/src/transformers/models/auto/tokenization_auto.py
index 7e15ca1741ab..b7f29a92270a 100644
--- a/src/transformers/models/auto/tokenization_auto.py
+++ b/src/transformers/models/auto/tokenization_auto.py
@@ -344,21 +344,34 @@
 MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS: set[str] = {
     "arctic",
     "chameleon",
-    "deepseek_vl",
-    "deepseek_vl_v2",
-    "deepseek_vl_hybrid",
+    "chatlm",
     "deepseek_v2",
     "deepseek_v3",
+    "deepseek_vl",
+    "deepseek_vl_hybrid",
+    "deepseek_vl_v2",
     "fuyu",
+    "h2ovl_chat",
     "hyperclovax_vlm",
     "internlm2",
-    "janus",
+    "internvl_chat",
     "jamba",
+    "janus",
+    "kimi_k25",
     "llava",
     "llava_next",
+    "minicpmv",
+    "minimax_m2",
     "modernbert",
+    "molmo",
+    "molmo2",
+    "nemotron",
+    "nvfp4",
     "opencua",
+    "openvla",
     "phi3",
+    "phi3_v",
+    "phimoe",
     "step3p5",
     "vipllava",
 }
diff --git a/src/transformers/models/llama4/configuration_llama4.py b/src/transformers/models/llama4/configuration_llama4.py
index 10a3361861db..c436511bdeeb 100644
--- a/src/transformers/models/llama4/configuration_llama4.py
+++ b/src/transformers/models/llama4/configuration_llama4.py
@@ -166,7 +166,7 @@ class Llama4TextConfig(PreTrainedConfig):
     no_rope_layers: list[int] | None = None
     no_rope_layer_interval: int = 4
     attention_chunk_size: int = 8192
-    layer_types: list[int] | None = None
+    layer_types: list[str] | None = None
     attn_temperature_tuning: bool = True
     floor_scale: int = 8192
     attn_scale: float = 0.1

PATCH

echo "Patch applied successfully."
