#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if static activation support is already added
if grep -q 'gate_up_proj_activation_scale' src/transformers/integrations/finegrained_fp8.py; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/integrations/finegrained_fp8.py b/src/transformers/integrations/finegrained_fp8.py
index 8b706ffc92ed..709cc1c46778 100644
--- a/src/transformers/integrations/finegrained_fp8.py
+++ b/src/transformers/integrations/finegrained_fp8.py
@@ -186,7 +186,29 @@ def w8a8_fp8_matmul(
     if _supports_cutlass(A, B, block_size, output_dtype):
         return w8a8_block_fp8_matmul_cutlass(A, B, As, Bs, output_dtype)

-    # Fall back to Triton
+    # Ensure correct CUDA device context for Triton JIT on multi-GPU
+    torch.cuda.set_device(A.device)
+
+    # TODO(kernels-community/finegrained-fp8): remove once the hub tensor-scale kernel
+    # handles non-power-of-2 dimensions internally (e.g. N=320 for MLA kv_a_proj).
+    # The kernel uses tl.arange(0, N) which requires N to be a power of 2.
+    if block_size is None:
+        N, K = B.shape
+        n_needs_pad = (N % 128 != 0) and (N & (N - 1)) != 0
+        k_needs_pad = (K % 128 != 0) and (K & (K - 1)) != 0
+        if n_needs_pad or k_needs_pad:
+            orig_N = N
+            if n_needs_pad:
+                pad_n = ((N + 127) // 128 * 128) - N
+                B = F.pad(B, [0, 0, 0, pad_n])
+            if k_needs_pad:
+                pad_k = ((K + 127) // 128 * 128) - K
+                B = F.pad(B, [0, pad_k])
+                A = F.pad(A, [0, pad_k])
+            kernel = _get_triton_kernel()
+            result = kernel.w8a8_fp8_matmul(A, B, As, Bs, None, output_dtype)
+            return result[..., :orig_N]
+
     kernel = _get_triton_kernel()
     return kernel.w8a8_fp8_matmul(A, B, As, Bs, block_size, output_dtype)

@@ -274,6 +296,7 @@ def fp8_batched_mm_experts_forward(
 ) -> torch.Tensor:
     kernel = _get_triton_kernel()
     device = hidden_states.device
+    torch.cuda.set_device(device)
     num_top_k = top_k_index.size(-1)
     num_tokens = hidden_states.size(0)
     hidden_dim = hidden_states.size(-1)
@@ -330,6 +353,7 @@ def fp8_grouped_mm_experts_forward(
     top_k_weights: torch.Tensor,
 ) -> torch.Tensor:
     kernel = _get_triton_kernel()
+    torch.cuda.set_device(hidden_states.device)
     device = hidden_states.device
     num_top_k = top_k_index.size(-1)
     num_tokens = hidden_states.size(0)
@@ -414,9 +438,6 @@ def __init__(
         assert has_bias is False, (
             "FP8Experts does not support bias for now, please open an issue if you want this feature"
         )
-        assert activation_scheme == "dynamic", (
-            "Only dynamic activation quantization is supported for now, please open an issue if you want others"
-        )

         self.config = config
         self.has_bias = has_bias
@@ -457,6 +478,10 @@ def __init__(
         )
         self.register_parameter("down_proj_bias", None)

+        if self.activation_scheme == "static":
+            self.gate_up_proj_activation_scale = nn.Parameter(torch.ones(self.num_experts, dtype=torch.float32))
+            self.down_proj_activation_scale = nn.Parameter(torch.ones(self.num_experts, dtype=torch.float32))
+
         self.act_fn = ACT2FN[config.hidden_act]

     def _apply_gate(self, gate_up: torch.Tensor) -> torch.Tensor:
@@ -481,26 +506,48 @@ def forward(

             top_k_pos, token_idx = torch.where(expert_mask[expert_idx])
             current_state = hidden_states[token_idx]
+            gate_up_act_scale = (
+                self.gate_up_proj_activation_scale[expert_idx] if self.activation_scheme == "static" else None
+            )
             proj_out = self.linear(
                 current_state,
                 self.gate_up_proj[expert_idx] if self.has_gate else self.up_proj[expert_idx],
                 self.gate_up_proj_scale_inv[expert_idx] if self.has_gate else self.up_proj_scale_inv[expert_idx],
+                activation_scale=gate_up_act_scale,
             )
             proj_out = self._apply_gate(proj_out) if self.has_gate else self.act_fn(proj_out)
-            proj_out = self.linear(proj_out, self.down_proj[expert_idx], self.down_proj_scale_inv[expert_idx])
+            down_act_scale = (
+                self.down_proj_activation_scale[expert_idx] if self.activation_scheme == "static" else None
+            )
+            proj_out = self.linear(
+                proj_out,
+                self.down_proj[expert_idx],
+                self.down_proj_scale_inv[expert_idx],
+                activation_scale=down_act_scale,
+            )
             routing_weights = top_k_weights[token_idx, top_k_pos, None]
             weighted_out = proj_out * routing_weights.to(proj_out.dtype)
             final_hidden_states.index_add_(0, token_idx, weighted_out.to(final_hidden_states.dtype))
         return final_hidden_states.to(hidden_states.dtype)

-    def linear(self, input: torch.Tensor, weight: torch.Tensor, weight_scale_inv: torch.Tensor) -> torch.Tensor:
+    def linear(
+        self,
+        input: torch.Tensor,
+        weight: torch.Tensor,
+        weight_scale_inv: torch.Tensor,
+        activation_scale: torch.Tensor | None = None,
+    ) -> torch.Tensor:
         if weight.element_size() > 1:
             return F.linear(input, weight, None)

-        kernel = _get_triton_kernel()
-        qinput, scale = kernel.fp8_act_quant(
-            input, self.block_size[1] if self.block_size is not None else input.shape[-1]
-        )
+        if self.activation_scheme == "static" and activation_scale is not None:
+            scale = activation_scale.to(torch.float32)
+            qinput = (input / scale).clamp(min=_FP8_MIN, max=_FP8_MAX).to(_FP8_DTYPE)
+        else:
+            kernel = _get_triton_kernel()
+            qinput, scale = kernel.fp8_act_quant(
+                input, self.block_size[1] if self.block_size is not None else input.shape[-1]
+            )
         output = w8a8_fp8_matmul(
             qinput,
             weight,

PATCH

echo "Patch applied successfully."
