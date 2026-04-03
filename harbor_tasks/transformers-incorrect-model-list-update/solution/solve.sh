#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency check
if grep -q '"h2ovl_chat"' src/transformers/models/auto/tokenization_auto.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --3way - <<'PATCH'
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
diff --git a/tests/test_tokenizers_backend_mixin.py b/tests/test_tokenizers_backend_mixin.py
index 8edb02fe079d..657166e08ee1 100644
--- a/tests/test_tokenizers_backend_mixin.py
+++ b/tests/test_tokenizers_backend_mixin.py
@@ -527,6 +527,14 @@ class TokenizersBackendV5RoundtripIntegrationTest(unittest.TestCase):
     EXPECTED_DISHAM993_ELECTRICAL_NER_MODERNBERT_BASE = "This is a test 😊\nI was born in 92000, and this is falsé.\n生活的真谛是\nHi  Hello\nHi   Hello\n\n \n  \n Hello\n<s>\nhi<s>there\nThe following string should be properly encoded: Hello.\nBut ird and ปี   ird   ด\nHey how are you doing"
     EXPECTED_DEEPSEEK_AI_DEEPSEEK_R1 = "This is a test 😊\nI was born in 92000, and this is falsé.\n生活的真谛是\nHi  Hello\nHi   Hello\n\n \n  \n Hello\n<s>\nhi<s>there\nThe following string should be properly encoded: Hello.\nBut ird and ปี   ird   ด\nHey how are you doing"
     EXPECTED_REDHATAI_DEEPSEEK_CODER_V2_LITE_INSTRUCT_FP8 = "This is a test 😊\nI was born in 92000, and this is falsé.\n生活的真谛是\nHi  Hello\nHi   Hello\n\n \n  \n Hello\n<s>\nhi<s>there\nThe following string should be properly encoded: Hello.\nBut ird and ปี   ird   ด\nHey how are you doing"
+    EXPECTED_H2OAI_H2OVL_MISSISSIPPI_2B = "This is a test 😊\nI was born in 92000, and this is falsé.\n生活的真谛是\nHi  Hello\nHi   Hello\n\n \n  \n Hello\n \nhi there\nThe following string should be properly encoded: Hello.\nBut ird and ปี   ird   ด\nHey how are you doing"
+    EXPECTED_OPENGVLAB_INTERNVL2_4B = "This is a test 😊\nI was born in 92000, and this is falsé.\n生活的真谛是\nHi  Hello\nHi   Hello\n\n \n  \n Hello\n\nhithere\nThe following string should be properly encoded: Hello.\nBut ird and ปี   ird   ด\nHey how are you doing"
+    EXPECTED_INTEL_MINIMAX_M25_INT4_AUTOROUND = "This is a test 😊\nI was born in 92000, and this is falsé.\n生活的真谛是\nHi  Hello\nHi   Hello\n\n \n  \n Hello\n<s>\nhi<s>there\nThe following string should be properly encoded: Hello.\nBut ird and ปี   ird   ด\nHey how are you doing"
+    EXPECTED_FRIENDLIAI_MOLMO_7B_O_0924 = "This is a test 😊\nI was born in 92000, and this is falsé.\n生活的真谛是\nHi  Hello\nHi   Hello\n\n \n  \n Hello\n<s>\nhi<s>there\nThe following string should be properly encoded: Hello.\nBut ird and ปี   ird   ด\nHey how are you doing"
+    EXPECTED_LUKEALONSO_QWEN35_397B_A17B_NVFP4 = "This is a test 😊\nI was born in 92000, and this is falsé.\n生活的真谛是\nHi  Hello\nHi   Hello\n\n \n  \n Hello\n<s>\nhi<s>there\nThe following string should be properly encoded: Hello.\nBut ird and ปี   ird   ด\nHey how are you doing"
+    EXPECTED_EMBODIED_COT_ECOT_OPENVLA_7B_BRIDGE = "This is a test 😊\nI was born in 92000, and this is falsé.\n生活的真谛是\nHi  Hello\nHi   Hello\n\n \n  \n Hello\n\nhithere\nThe following string should be properly encoded: Hello.\nBut ird and ปี   ird   ด\nHey how are you doing"
+    EXPECTED_DEEPGLINT_AI_UNIME_PHI35_V_42B = "This is a test 😊\nI was born in 92000, and this is falsé.\n生活的真谛是\nHi  Hello\nHi   Hello\n\n \n  \n Hello\n\nhithere\nThe following string should be properly encoded: Hello.\nBut ird and ปี   ird   ด\nHey how are you doing"
+    EXPECTED_1024M_PHI_35_MOE_4BIT_FP4 = "This is a test 😊\nI was born in 92000, and this is falsé.\n生活的真谛是\nHi  Hello\nHi   Hello\n\n \n  \n Hello\n\nhithere\nThe following string should be properly encoded: Hello.\nBut ird and ปี   ird   ด\nHey how are you doing"

     TOKENIZERS_BACKEND_V5_MODELS_WITH_EXPECTED = [
         ("xlangai/OpenCUA-7B", EXPECTED_XLANGAI_OPENCUA_7B),
@@ -542,6 +550,14 @@ class TokenizersBackendV5RoundtripIntegrationTest(unittest.TestCase):
             "RedHatAI/DeepSeek-Coder-V2-Lite-Instruct-FP8",
             EXPECTED_REDHATAI_DEEPSEEK_CODER_V2_LITE_INSTRUCT_FP8,
         ),
+        ("h2oai/h2ovl-mississippi-2b", EXPECTED_H2OAI_H2OVL_MISSISSIPPI_2B),
+        ("OpenGVLab/InternVL2-4B", EXPECTED_OPENGVLAB_INTERNVL2_4B),
+        ("Intel/MiniMax-M2.5-int4-AutoRound", EXPECTED_INTEL_MINIMAX_M25_INT4_AUTOROUND),
+        ("FriendliAI/Molmo-7B-O-0924", EXPECTED_FRIENDLIAI_MOLMO_7B_O_0924),
+        ("lukealonso/Qwen3.5-397B-A17B-NVFP4", EXPECTED_LUKEALONSO_QWEN35_397B_A17B_NVFP4),
+        ("Embodied-CoT/ecot-openvla-7b-bridge", EXPECTED_EMBODIED_COT_ECOT_OPENVLA_7B_BRIDGE),
+        ("DeepGlint-AI/UniME-Phi3.5-V-4.2B", EXPECTED_DEEPGLINT_AI_UNIME_PHI35_V_42B),
+        ("1024m/Phi-3.5-MoE-4bit-fp4", EXPECTED_1024M_PHI_35_MOE_4BIT_FP4),
     ]

     @parameterized.expand(TOKENIZERS_BACKEND_V5_MODELS_WITH_EXPECTED)
PATCH

echo "Patch applied successfully."
