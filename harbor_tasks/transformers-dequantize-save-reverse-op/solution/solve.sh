#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if _IdentityOp already exists in core_model_loading.py, skip
if grep -q '_IdentityOp' src/transformers/core_model_loading.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/core_model_loading.py b/src/transformers/core_model_loading.py
index 9bcd625d2840..ce0f2d9cec9b 100644
--- a/src/transformers/core_model_loading.py
+++ b/src/transformers/core_model_loading.py
@@ -101,6 +101,17 @@ def reverse_op(self) -> ConversionOps:
         raise NotImplementedError


+class _IdentityOp(ConversionOps):
+    """Pass-through reverse op for dequantize operations.
+
+    Dequantized weights are already in their target dtype and should be
+    saved as-is without any conversion.
+    """
+
+    def convert(self, input_dict: dict[str, Any], **kwargs) -> dict[str, Any]:
+        return input_dict
+
+
 class Chunk(ConversionOps):
     """Split a tensor along ``dim`` into equally sized chunks."""

diff --git a/src/transformers/integrations/finegrained_fp8.py b/src/transformers/integrations/finegrained_fp8.py
index 709cc1c46778..cc086534950b 100644
--- a/src/transformers/integrations/finegrained_fp8.py
+++ b/src/transformers/integrations/finegrained_fp8.py
@@ -17,7 +17,7 @@
 from torch.nn import functional as F

 from ..activations import ACT2FN
-from ..core_model_loading import ConversionOps
+from ..core_model_loading import ConversionOps, _IdentityOp
 from ..quantizers.quantizers_utils import should_convert_module
 from ..utils import is_kernels_available, is_torch_available, logging
 from .hub_kernels import get_kernel
@@ -752,3 +752,7 @@ def convert(
         return {
             full_layer_name: dequantized.reshape(quantized.shape),
         }
+
+    @property
+    def reverse_op(self) -> "ConversionOps":
+        return _IdentityOp()
diff --git a/src/transformers/integrations/metal_quantization.py b/src/transformers/integrations/metal_quantization.py
index 6ade40af53f5..ea23a5496c6a 100644
--- a/src/transformers/integrations/metal_quantization.py
+++ b/src/transformers/integrations/metal_quantization.py
@@ -33,7 +33,7 @@
 which computes ``y = x @ dequant(weight).T``, identical to ``nn.Linear``.
 """

-from ..core_model_loading import ConversionOps
+from ..core_model_loading import ConversionOps, _IdentityOp
 from ..quantizers.quantizers_utils import should_convert_module
 from ..utils import is_torch_available, logging

@@ -294,3 +294,7 @@ def convert(self, input_dict: dict, full_layer_name: str | None = None, **kwargs

         w_deq = _affine_dequantize_tensor(quantized, scales, qbiases, group_size, bits)
         return {full_layer_name: w_deq.to(scales.dtype)}
+
+    @property
+    def reverse_op(self) -> "ConversionOps":
+        return _IdentityOp()
diff --git a/src/transformers/integrations/mxfp4.py b/src/transformers/integrations/mxfp4.py
index 6569f3f93bea..67d9420659af 100644
--- a/src/transformers/integrations/mxfp4.py
+++ b/src/transformers/integrations/mxfp4.py
@@ -20,7 +20,7 @@
     from torch import nn
 from contextlib import contextmanager

-from ..core_model_loading import ConversionOps
+from ..core_model_loading import ConversionOps, _IdentityOp
 from ..quantizers.quantizers_utils import get_module_from_name, should_convert_module


@@ -145,6 +145,10 @@ def convert(
         dequantized = dequantize_convertops(param_data[f"{proj}_blocks"], param_data[f"{proj}_scales"])
         return {full_layer_name: dequantized}

+    @property
+    def reverse_op(self) -> "ConversionOps":
+        return _IdentityOp()
+

 class Mxfp4Deserialize(ConversionOps):
     def __init__(self, hf_quantizer):

PATCH

echo "Patch applied successfully."
