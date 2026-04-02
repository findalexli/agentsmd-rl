#!/usr/bin/env bash
set -euo pipefail

FILE="/workspace/torch/_inductor/fx_passes/post_grad.py"

# Idempotency: check if already patched
if grep -q 'torch.bfloat16, torch.float16' "$FILE" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/torch/_inductor/fx_passes/post_grad.py b/torch/_inductor/fx_passes/post_grad.py
index 427a6918a9cea..5c560b9dda4b7 100644
--- a/torch/_inductor/fx_passes/post_grad.py
+++ b/torch/_inductor/fx_passes/post_grad.py
@@ -1517,6 +1517,11 @@ def should_prefer_unfused_addmm(match):
     extra_check=should_prefer_unfused_addmm,
 )
 def unfuse_bias_add_to_pointwise(match: Match, mat1, mat2, *, inp, alpha, beta):
+    # Unfusing addmm introduces an extra bf16/fp16 truncation at the mm output
+    # that compounds through deep models and causes accuracy failures.
+    if inp.meta["val"].dtype in (torch.bfloat16, torch.float16):
+        return
+
     def repl(inp, x1, x2, alpha, beta):
         mm_result = x1 @ x2
         if alpha != 1:

PATCH

echo "Patch applied successfully."
