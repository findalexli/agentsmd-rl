#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if the fix is already applied, skip
if grep -q '_get_weight_params' vllm/model_executor/kernels/linear/mixed_precision/cpu.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/model_executor/kernels/linear/mixed_precision/cpu.py b/vllm/model_executor/kernels/linear/mixed_precision/cpu.py
index afd41b72f126..72e562012373 100644
--- a/vllm/model_executor/kernels/linear/mixed_precision/cpu.py
+++ b/vllm/model_executor/kernels/linear/mixed_precision/cpu.py
@@ -58,28 +58,29 @@ def can_implement(cls, c: MPLinearLayerConfig) -> tuple[bool, str | None]:
         return True, None

     # note assumes that
-    #  `weight_packed` is: {input_dim = 0, output_dim = 1, packed_dim = 0}
-    #  `weight_scale`  is: {input_dim = 0, output_dim = 1}
-    #  `weight_zp`     is: {input_dim = 0, output_dim = 1, packed_dim = 1}
+    #  `weight_packed` is: {input_dim = 0, output_dim = 1, packed_dim = 0} (marlin)
+    #                  or: {input_dim = 1, output_dim = 0, packed_dim = 1} (CT)
+    #  `weight_scale`  is: {input_dim = 0, output_dim = 1} (marlin)
+    #                  or: {input_dim = 1, output_dim = 0} (CT)
+    #  `weight_zp`     is: {input_dim = 0, output_dim = 1, packed_dim = 1} (marlin)
+    #                  or: {input_dim = 1, output_dim = 0, packed_dim = 0} (CT)
     def _process_gptq_weights(self, layer: torch.nn.Module):
-        packed_weight = layer.qweight.data
+        packed_weight = getattr(layer, self.w_q_name)
+        assert packed_weight.input_dim == packed_weight.packed_dim
+        is_ct_format = packed_weight.input_dim == 1
+        if is_ct_format:
+            packed_weight = packed_weight.t()
         bits = self.config.weight_type.mantissa
         pack_factor = 32 // bits
-        p_w_k, p_w_n = packed_weight.size()
+        p_w_k, _ = packed_weight.size()
         input_size = p_w_k * pack_factor
-        output_size = p_w_n
-        isa_hint = _get_isa_hint(layer.scales.dtype)
+        isa_hint = _get_isa_hint(getattr(layer, self.w_s_name).dtype)
         layer.isa_hint = isa_hint

-        layer.qzeros = None
-        if not self.config.has_g_idx:
-            layer.g_idx = None
-
         # convert input dim packed to output dim packed
         weight = unpack_quantized_values_into_int32(
-            packed_weight, self.config.weight_type, 1
-        ).view(p_w_k, p_w_n, pack_factor)
-        weight = weight.permute(0, 2, 1).reshape(input_size, output_size).contiguous()
+            packed_weight, self.config.weight_type, 0
+        )
         weight = pack_quantized_values_into_int32(weight, self.config.weight_type, 1)
         # make 16 output channel as a block and transpose to the make
         # the block contiguous
@@ -89,10 +90,29 @@ def _process_gptq_weights(self, layer: torch.nn.Module):
             .reshape(-1, input_size * 16 // pack_factor)
             .contiguous()
         )
-        layer.qweight.data = weight
+        getattr(layer, self.w_q_name).data = weight
+
+        # transpose scale, zp for CT format
+        if is_ct_format:
+            scales = getattr(layer, self.w_s_name)
+            scales.data = scales.t().contiguous()
+            if self.config.zero_points:
+                assert self.w_zp_name
+                zp = getattr(layer, self.w_zp_name)
+                zp.data = zp.t().contiguous()

     def process_weights_after_loading(self, layer: torch.nn.Module):
-        if not self.config.zero_points:
+        if (not self.config.zero_points) and (self.w_zp_name is not None):
+            setattr(layer, self.w_zp_name, None)
+
+        if (not self.config.has_g_idx) and (self.w_gidx_name is not None):
+            setattr(layer, self.w_gidx_name, None)
+
+        w_input_dim = getattr(layer, self.w_q_name).input_dim
+        w_pack_dim = getattr(layer, self.w_q_name).packed_dim
+        quant_method = "gptq" if w_pack_dim == w_input_dim else "awq"
+
+        if quant_method == "gptq":
             # GPTQ
             self._process_gptq_weights(layer)
         else:
@@ -105,12 +125,13 @@ def apply_weights(
         x: torch.Tensor,
         bias: torch.Tensor | None = None,
     ) -> torch.Tensor:
+        w_q, w_s, w_zp, w_gidx = self._get_weight_params(layer)
         x = ops.cpu_gemm_wna16(
             input=x,
-            q_weight=layer.qweight,
-            scales=layer.scales,
-            zeros=layer.qzeros,
-            g_idx=layer.g_idx,
+            q_weight=w_q,
+            scales=w_s,
+            zeros=w_zp,
+            g_idx=w_gidx,
             bias=bias,
             pack_factor=8,  # 32 // 4
             isa_hint=layer.isa_hint,

PATCH

echo "Patch applied successfully."
