#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied
if grep -q '_detect_gfx95_quant_format' python/sglang/srt/models/deepseek_v2.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/python/sglang/srt/models/deepseek_v2.py b/python/sglang/srt/models/deepseek_v2.py
index 6fae78248777..5769e9b5e30e 100644
--- a/python/sglang/srt/models/deepseek_v2.py
+++ b/python/sglang/srt/models/deepseek_v2.py
@@ -1592,6 +1592,8 @@ class DeepseekV2DecoderLayer(nn.Module):
             config.hidden_size, eps=config.rms_norm_eps
         )

+        self._gfx95_quant_format = self._detect_gfx95_quant_format()
+
         if self.nsa_enable_prefill_cp:
             self.layer_communicator = NSACPLayerCommunicator(
                 layer_scatter_modes=self.layer_scatter_modes,
@@ -1615,6 +1617,20 @@ class DeepseekV2DecoderLayer(nn.Module):
                 qkv_latent_func=self.self_attn.prepare_qkv_latent,
             )

+    def _detect_gfx95_quant_format(self) -> str:
+        if not _is_gfx95_supported:
+            return ""
+        weight = getattr(
+            getattr(self.self_attn, "fused_qkv_a_proj_with_mqa", None), "weight", None
+        )
+        if weight is None:
+            return ""
+        if weight.dtype == torch.uint8:
+            return "mxfp4"
+        if weight.dtype == getattr(torch, "float8_e4m3fn", None):
+            return "fp8"
+        return ""
+
     def _is_layer_sparse(self, layer_id: int, is_nextn: bool) -> bool:
         return is_nextn or (
             self.config.n_routed_experts is not None
@@ -1632,38 +1648,11 @@ class DeepseekV2DecoderLayer(nn.Module):
         gemm_output_zero_allocator: BumpAllocator = None,
         llama_4_scaling: Optional[torch.Tensor] = None,
     ) -> torch.Tensor:
-        quant_format = (
-            "mxfp4"
-            if (
-                _is_gfx95_supported
-                and getattr(self.self_attn, "fused_qkv_a_proj_with_mqa", None)
-                is not None
-                and getattr(self.self_attn.fused_qkv_a_proj_with_mqa, "weight", None)
-                is not None
-                and self.self_attn.fused_qkv_a_proj_with_mqa.weight.dtype == torch.uint8
-            )
-            else (
-                "fp8"
-                if (
-                    _is_gfx95_supported
-                    and getattr(self.self_attn, "fused_qkv_a_proj_with_mqa", None)
-                    is not None
-                    and getattr(
-                        self.self_attn.fused_qkv_a_proj_with_mqa, "weight", None
-                    )
-                    is not None
-                    and self.self_attn.fused_qkv_a_proj_with_mqa.weight.dtype
-                    == getattr(torch, "float8_e4m3fn", None)
-                )
-                else ""
-            )
-        )
-
         hidden_states, residual = self.layer_communicator.prepare_attn(
             hidden_states,
             residual,
             forward_batch,
-            quant_format,
+            self._gfx95_quant_format,
         )

         hidden_states = self.self_attn(

PATCH

echo "Patch applied successfully."
