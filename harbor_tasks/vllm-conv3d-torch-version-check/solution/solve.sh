#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if fix is already applied
if grep -q 'is_torch_equal_or_newer' vllm/model_executor/layers/conv.py 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/model_executor/layers/conv.py b/vllm/model_executor/layers/conv.py
index f4709f2f4d80..51314263b735 100644
--- a/vllm/model_executor/layers/conv.py
+++ b/vllm/model_executor/layers/conv.py
@@ -10,7 +10,7 @@
 import torch.nn.functional as F

 from vllm.model_executor.custom_op import CustomOp
-from vllm.utils.torch_utils import is_torch_equal
+from vllm.utils.torch_utils import is_torch_equal_or_newer


 class ConvLayerBase(CustomOp):
@@ -252,11 +252,12 @@ def forward_native(self, x: torch.Tensor) -> torch.Tensor:
             return self._forward_conv(x)

     def forward_cuda(self, x: torch.Tensor) -> torch.Tensor:
-        # PyTorch2.9.0 disabled CUDNN's Conv3D, which caused a
+        # PyTorch 2.9.0+ disabled CUDNN's Conv3D, which caused a
         # significant performance regression.
         # See: https://github.com/vllm-project/vllm/issues/27406
         # and https://github.com/pytorch/pytorch/issues/166122
+        # and https://github.com/huggingface/transformers/pull/45041
         # By default, we use CUDNN's convolution ops with optimization.
-        if self.enable_linear and (is_torch_equal("2.9.0") or is_torch_equal("2.9.1")):
+        if self.enable_linear and is_torch_equal_or_newer("2.9.0"):
             return self._forward_mulmat(x)
         return self._forward_conv(x)

PATCH

echo "Fix applied successfully."
