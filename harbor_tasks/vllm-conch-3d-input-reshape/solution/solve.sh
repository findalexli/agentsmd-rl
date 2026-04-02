#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Idempotency: check if fix is already applied
if grep -q 'x_2d = x.reshape(-1, x.shape\[-1\])' vllm/model_executor/kernels/linear/mixed_precision/conch.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/model_executor/kernels/linear/mixed_precision/conch.py b/vllm/model_executor/kernels/linear/mixed_precision/conch.py
index cd371581be0c..34dad0194ff9 100644
--- a/vllm/model_executor/kernels/linear/mixed_precision/conch.py
+++ b/vllm/model_executor/kernels/linear/mixed_precision/conch.py
@@ -134,8 +134,11 @@ def apply_weights(
         if group_size == -1:
             group_size = x.shape[-1]

+        x_2d = x.reshape(-1, x.shape[-1])
+        out_shape = x.shape[:-1] + (self.config.partition_weight_shape[1],)
+
         output = mixed_precision_gemm(
-            x=x,
+            x=x_2d,
             w_q_packed=w_q.data,
             w_s=w_s.data,
             w_zp=w_zp.data if w_zp is not None else None,
@@ -147,4 +150,4 @@ def apply_weights(
         if bias is not None:
             output.add_(bias)  # In-place add

-        return output
+        return output.reshape(out_shape)

PATCH

echo "Patch applied successfully."
