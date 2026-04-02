#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotency check: if fix is already applied, exit
if grep -q '"conv1d" not in key' tools/convert_hf_to_fp8.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/tools/convert_hf_to_fp8.py b/tools/convert_hf_to_fp8.py
index 98eebce01b..5294140d5a 100644
--- a/tools/convert_hf_to_fp8.py
+++ b/tools/convert_hf_to_fp8.py
@@ -134,6 +134,11 @@ def process_file(input_path, output_path, filename, strategy, block_size, result
             and "lm_head" not in key
             and "eh_proj" not in key
             and "weights_proj" not in key
+            and "conv1d" not in key
+            and "A_log" not in key
+            and "dt_bias" not in key
+            and "in_proj_a" not in key
+            and "in_proj_b" not in key
         ):
             qw, s = quant_fp8(weights[key], strategy, block_size)
             q_weights[key] = qw

PATCH

echo "Patch applied successfully."
