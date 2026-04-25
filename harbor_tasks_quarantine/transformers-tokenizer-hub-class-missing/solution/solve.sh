#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency check: if deepseek_v2 is already in the set, patch was applied
if grep -q '"deepseek_v2"' src/transformers/models/auto/tokenization_auto.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/models/auto/tokenization_auto.py b/src/transformers/models/auto/tokenization_auto.py
index 4faaa9844315..468211d4c879 100644
--- a/src/transformers/models/auto/tokenization_auto.py
+++ b/src/transformers/models/auto/tokenization_auto.py
@@ -346,6 +346,8 @@
     "deepseek_vl",
     "deepseek_vl_v2",
     "deepseek_vl_hybrid",
+    "deepseek_v2",
+    "deepseek_v3",
     "fuyu",
     "hyperclovax_vlm",
     "internlm2",
@@ -353,6 +355,7 @@
     "jamba",
     "llava",
     "llava_next",
+    "modernbert",
     "opencua",
     "phi3",
     "step3p5",

PATCH

echo "Patch applied successfully."
