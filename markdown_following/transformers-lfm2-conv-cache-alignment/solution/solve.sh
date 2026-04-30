#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if already applied
if grep -q 'has_previous_state' src/transformers/models/lfm2/modeling_lfm2.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/models/lfm2/modeling_lfm2.py b/src/transformers/models/lfm2/modeling_lfm2.py
index c6a9007a36c1..f087ec1cd4a6 100644
--- a/src/transformers/models/lfm2/modeling_lfm2.py
+++ b/src/transformers/models/lfm2/modeling_lfm2.py
@@ -179,8 +179,10 @@ def __init__(
         self.max_batch_size = max_batch_size
         self.layer_types = config.layer_types
         self.first_attention_layer = self.layer_types.index("full_attention")
+        self.last_conv_layer = len(self.layer_types) - self.layer_types[::-1].index("conv") - 1
         self.conv_L_cache = config.conv_L_cache
         self._dtype = dtype
+        self.has_previous_state = False

         self.conv_cache: list[torch.Tensor] = []
         device = torch.device(device) if device is not None else None
@@ -230,6 +232,24 @@ def update(

         return self.key_cache[layer_idx], self.value_cache[layer_idx]

+    def update_conv_state(
+        self, layer_idx: int, new_conv_state: torch.Tensor, cache_init: bool = False
+    ) -> torch.Tensor:
+        # Technically, those update are not logically correct if the prefill is smaller than `conv_kernel_size`,
+        # as it will `roll` anyway in the first decoding step even though it should `roll` ONLY if the cache is already full.
+        # But since `conv_kernel_size=4` in practice, it's almost impossible to have a smaller prefill so it's mostly fine for now
+        if cache_init:
+            self.conv_cache[layer_idx] = new_conv_state.to(self.conv_cache[layer_idx].device)
+        else:
+            self.conv_cache[layer_idx] = self.conv_cache[layer_idx].roll(shifts=-1, dims=-1)
+            self.conv_cache[layer_idx][:, :, -1] = new_conv_state[:, :, -1].to(self.conv_cache[layer_idx].device)
+
+        # If last layer is updated, set the flag
+        if layer_idx == self.last_conv_layer:
+            self.has_previous_state = True
+
+        return self.conv_cache[layer_idx]
+
     def reorder_cache(self, beam_idx: torch.LongTensor):
         """Reorders the cache for beam search, given the selected beam indices."""
         for layer_idx in range(len(self.key_cache)):
@@ -280,6 +300,7 @@ def __len__(self) -> int:
         return len(self.key_cache)

     def reset(self):
+        self.has_previous_state = False
         for layer_idx in range(len(self.conv_cache)):
             # In-place ops prevent breaking the static address
             self.conv_cache[layer_idx].zero_()
@@ -459,22 +480,14 @@ def cuda_kernels_forward(
         past_key_values: Lfm2HybridConvCache | None = None,
         attention_mask: torch.Tensor | None = None,
     ):
-        seqlen = x.shape[1]
         x = apply_mask_to_padding_states(x, attention_mask)
         BCx = self.in_proj(x).transpose(-1, -2)
         B, C, x = BCx.chunk(3, dim=-2)

         Bx = B * x

-        # Note: we may or may not have to substract the current seq_len here as the cache may or may not be already updated
-        # by the current layer
-        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
-        # In this case, the cache was already updated and we need to subtract seq_len to get the correct past length
-        if "full_attention" in self.config.layer_types[: self.layer_idx]:
-            past_seen_tokens = past_seen_tokens - seqlen
-
         conv_weights = self.conv.weight.view(self.conv.weight.size(0), self.conv.weight.size(2))
-        if past_seen_tokens > 0:
+        if past_key_values is not None and past_key_values.has_previous_state:
             conv_out = causal_conv1d_update(
                 Bx.squeeze(-1),
                 past_key_values.conv_cache[self.layer_idx],
@@ -486,7 +499,7 @@ def cuda_kernels_forward(
         else:
             if past_key_values is not None:
                 conv_state = nn.functional.pad(Bx, (self.L_cache - Bx.shape[-1], 0))
-                past_key_values.conv_cache[self.layer_idx].copy_(conv_state)
+                past_key_values.update_conv_state(self.layer_idx, conv_state, cache_init=True)

             conv_out = causal_conv1d_fn(Bx, conv_weights, self.conv.bias, activation=None)

@@ -508,20 +521,8 @@ def slow_forward(

         Bx = B * x

-        # Note: we may or may not have to substract the current seq_len here as the cache may or may not be already updated
-        # by the current layer
-        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
-        # In this case, the cache was already updated and we need to subtract seq_len to get the correct past length
-        if "full_attention" in self.config.layer_types[: self.layer_idx]:
-            past_seen_tokens = past_seen_tokens - seqlen
-
-        if past_seen_tokens > 0:
-            conv_state = past_key_values.conv_cache[self.layer_idx]
-            positions = torch.arange(seqlen, device=conv_state.device) + past_seen_tokens
-            positions = positions.clamp(0, self.L_cache - 1)
-            conv_state = conv_state.roll(shifts=-1, dims=-1)
-            conv_state[:, :, positions] = Bx.to(device=conv_state.device, dtype=conv_state.dtype)
-            past_key_values.conv_cache[self.layer_idx].copy_(conv_state)
+        if past_key_values is not None and past_key_values.has_previous_state:
+            conv_state = past_key_values.update_conv_state(self.layer_idx, Bx, cache_init=False)
             conv_out = torch.sum(conv_state.to(Bx.device) * self.conv.weight[:, 0, :], dim=-1)
             if self.bias:
                 conv_out += self.conv.bias
@@ -530,7 +531,7 @@ def slow_forward(
         else:
             if past_key_values is not None:
                 conv_state = nn.functional.pad(Bx, (self.L_cache - Bx.shape[-1], 0))
-                past_key_values.conv_cache[self.layer_idx].copy_(conv_state)
+                conv_state = past_key_values.update_conv_state(self.layer_idx, conv_state, cache_init=True)

             conv_out = self.conv(Bx)[..., :seqlen]

diff --git a/src/transformers/models/lfm2/modular_lfm2.py b/src/transformers/models/lfm2/modular_lfm2.py
index 1da4d837de4b..6b573ae02f59 100644
--- a/src/transformers/models/lfm2/modular_lfm2.py
+++ b/src/transformers/models/lfm2/modular_lfm2.py
@@ -107,8 +107,10 @@ def __init__(
         self.max_batch_size = max_batch_size
         self.layer_types = config.layer_types
         self.first_attention_layer = self.layer_types.index("full_attention")
+        self.last_conv_layer = len(self.layer_types) - self.layer_types[::-1].index("conv") - 1
         self.conv_L_cache = config.conv_L_cache
         self._dtype = dtype
+        self.has_previous_state = False

         self.conv_cache: list[torch.Tensor] = []
         device = torch.device(device) if device is not None else None
@@ -158,6 +160,24 @@ def update(

         return self.key_cache[layer_idx], self.value_cache[layer_idx]

+    def update_conv_state(
+        self, layer_idx: int, new_conv_state: torch.Tensor, cache_init: bool = False
+    ) -> torch.Tensor:
+        # Technically, those update are not logically correct if the prefill is smaller than `conv_kernel_size`,
+        # as it will `roll` anyway in the first decoding step even though it should `roll` ONLY if the cache is already full.
+        # But since `conv_kernel_size=4` in practice, it's almost impossible to have a smaller prefill so it's mostly fine for now
+        if cache_init:
+            self.conv_cache[layer_idx] = new_conv_state.to(self.conv_cache[layer_idx].device)
+        else:
+            self.conv_cache[layer_idx] = self.conv_cache[layer_idx].roll(shifts=-1, dims=-1)
+            self.conv_cache[layer_idx][:, :, -1] = new_conv_state[:, :, -1].to(self.conv_cache[layer_idx].device)
+
+        # If last layer is updated, set the flag
+        if layer_idx == self.last_conv_layer:
+            self.has_previous_state = True
+
+        return self.conv_cache[layer_idx]
+
     def reorder_cache(self, beam_idx: torch.LongTensor):
         """Reorders the cache for beam search, given the selected beam indices."""
         for layer_idx in range(len(self.key_cache)):
@@ -208,6 +228,7 @@ def __len__(self) -> int:
         return len(self.key_cache)

     def reset(self):
+        self.has_previous_state = False
         for layer_idx in range(len(self.conv_cache)):
             # In-place ops prevent breaking the static address
             self.conv_cache[layer_idx].zero_()
@@ -294,22 +315,14 @@ def cuda_kernels_forward(
         past_key_values: Lfm2HybridConvCache | None = None,
         attention_mask: torch.Tensor | None = None,
     ):
-        seqlen = x.shape[1]
         x = apply_mask_to_padding_states(x, attention_mask)
         BCx = self.in_proj(x).transpose(-1, -2)
         B, C, x = BCx.chunk(3, dim=-2)

         Bx = B * x

-        # Note: we may or may not have to substract the current seq_len here as the cache may or may not be already updated
-        # by the current layer
-        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
-        # In this case, the cache was already updated and we need to subtract seq_len to get the correct past length
-        if "full_attention" in self.config.layer_types[: self.layer_idx]:
-            past_seen_tokens = past_seen_tokens - seqlen
-
         conv_weights = self.conv.weight.view(self.conv.weight.size(0), self.conv.weight.size(2))
-        if past_seen_tokens > 0:
+        if past_key_values is not None and past_key_values.has_previous_state:
             conv_out = causal_conv1d_update(
                 Bx.squeeze(-1),
                 past_key_values.conv_cache[self.layer_idx],
@@ -321,7 +334,7 @@ def cuda_kernels_forward(
         else:
             if past_key_values is not None:
                 conv_state = nn.functional.pad(Bx, (self.L_cache - Bx.shape[-1], 0))
-                past_key_values.conv_cache[self.layer_idx].copy_(conv_state)
+                past_key_values.update_conv_state(self.layer_idx, conv_state, cache_init=True)

             conv_out = causal_conv1d_fn(Bx, conv_weights, self.conv.bias, activation=None)

@@ -343,20 +356,8 @@ def slow_forward(

         Bx = B * x

-        # Note: we may or may not have to substract the current seq_len here as the cache may or may not be already updated
-        # by the current layer
-        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
-        # In this case, the cache was already updated and we need to subtract seq_len to get the correct past length
-        if "full_attention" in self.config.layer_types[: self.layer_idx]:
-            past_seen_tokens = past_seen_tokens - seqlen
-
-        if past_seen_tokens > 0:
-            conv_state = past_key_values.conv_cache[self.layer_idx]
-            positions = torch.arange(seqlen, device=conv_state.device) + past_seen_tokens
-            positions = positions.clamp(0, self.L_cache - 1)
-            conv_state = conv_state.roll(shifts=-1, dims=-1)
-            conv_state[:, :, positions] = Bx.to(device=conv_state.device, dtype=conv_state.dtype)
-            past_key_values.conv_cache[self.layer_idx].copy_(conv_state)
+        if past_key_values is not None and past_key_values.has_previous_state:
+            conv_state = past_key_values.update_conv_state(self.layer_idx, Bx, cache_init=False)
             conv_out = torch.sum(conv_state.to(Bx.device) * self.conv.weight[:, 0, :], dim=-1)
             if self.bias:
                 conv_out += self.conv.bias
@@ -365,7 +366,7 @@ def slow_forward(
         else:
             if past_key_values is not None:
                 conv_state = nn.functional.pad(Bx, (self.L_cache - Bx.shape[-1], 0))
-                past_key_values.conv_cache[self.layer_idx].copy_(conv_state)
+                conv_state = past_key_values.update_conv_state(self.layer_idx, conv_state, cache_init=True)

             conv_out = self.conv(Bx)[..., :seqlen]

diff --git a/src/transformers/models/lfm2_moe/modeling_lfm2_moe.py b/src/transformers/models/lfm2_moe/modeling_lfm2_moe.py
index 619aa413ecc8..310982a04dc7 100644
--- a/src/transformers/models/lfm2_moe/modeling_lfm2_moe.py
+++ b/src/transformers/models/lfm2_moe/modeling_lfm2_moe.py
@@ -255,8 +255,10 @@ def __init__(
         self.max_batch_size = max_batch_size
         self.layer_types = config.layer_types
         self.first_attention_layer = self.layer_types.index("full_attention")
+        self.last_conv_layer = len(self.layer_types) - self.layer_types[::-1].index("conv") - 1
         self.conv_L_cache = config.conv_L_cache
         self._dtype = dtype
+        self.has_previous_state = False

         self.conv_cache: list[torch.Tensor] = []
         device = torch.device(device) if device is not None else None
@@ -306,6 +308,24 @@ def update(

         return self.key_cache[layer_idx], self.value_cache[layer_idx]

+    def update_conv_state(
+        self, layer_idx: int, new_conv_state: torch.Tensor, cache_init: bool = False
+    ) -> torch.Tensor:
+        # Technically, those update are not logically correct if the prefill is smaller than `conv_kernel_size`,
+        # as it will `roll` anyway in the first decoding step even though it should `roll` ONLY if the cache is already full.
+        # But since `conv_kernel_size=4` in practice, it's almost impossible to have a smaller prefill so it's mostly fine for now
+        if cache_init:
+            self.conv_cache[layer_idx] = new_conv_state.to(self.conv_cache[layer_idx].device)
+        else:
+            self.conv_cache[layer_idx] = self.conv_cache[layer_idx].roll(shifts=-1, dims=-1)
+            self.conv_cache[layer_idx][:, :, -1] = new_conv_state[:, :, -1].to(self.conv_cache[layer_idx].device)
+
+        # If last layer is updated, set the flag
+        if layer_idx == self.last_conv_layer:
+            self.has_previous_state = True
+
+        return self.conv_cache[layer_idx]
+
     def reorder_cache(self, beam_idx: torch.LongTensor):
         """Reorders the cache for beam search, given the selected beam indices."""
         for layer_idx in range(len(self.key_cache)):
@@ -356,6 +376,7 @@ def __len__(self) -> int:
         return len(self.key_cache)

     def reset(self):
+        self.has_previous_state = False
         for layer_idx in range(len(self.conv_cache)):
             # In-place ops prevent breaking the static address
             self.conv_cache[layer_idx].zero_()
@@ -535,22 +556,14 @@ def cuda_kernels_forward(
         past_key_values: Lfm2MoeHybridConvCache | None = None,
         attention_mask: torch.Tensor | None = None,
     ):
-        seqlen = x.shape[1]
         x = apply_mask_to_padding_states(x, attention_mask)
         BCx = self.in_proj(x).transpose(-1, -2)
         B, C, x = BCx.chunk(3, dim=-2)

         Bx = B * x

-        # Note: we may or may not have to substract the current seq_len here as the cache may or may not be already updated
-        # by the current layer
-        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
-        # In this case, the cache was already updated and we need to subtract seq_len to get the correct past length
-        if "full_attention" in self.config.layer_types[: self.layer_idx]:
-            past_seen_tokens = past_seen_tokens - seqlen
-
         conv_weights = self.conv.weight.view(self.conv.weight.size(0), self.conv.weight.size(2))
-        if past_seen_tokens > 0:
+        if past_key_values is not None and past_key_values.has_previous_state:
             conv_out = causal_conv1d_update(
                 Bx.squeeze(-1),
                 past_key_values.conv_cache[self.layer_idx],
@@ -562,7 +575,7 @@ def cuda_kernels_forward(
         else:
             if past_key_values is not None:
                 conv_state = nn.functional.pad(Bx, (self.L_cache - Bx.shape[-1], 0))
-                past_key_values.conv_cache[self.layer_idx].copy_(conv_state)
+                past_key_values.update_conv_state(self.layer_idx, conv_state, cache_init=True)

             conv_out = causal_conv1d_fn(Bx, conv_weights, self.conv.bias, activation=None)

@@ -584,20 +597,8 @@ def slow_forward(

         Bx = B * x

-        # Note: we may or may not have to substract the current seq_len here as the cache may or may not be already updated
-        # by the current layer
-        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
-        # In this case, the cache was already updated and we need to subtract seq_len to get the correct past length
-        if "full_attention" in self.config.layer_types[: self.layer_idx]:
-            past_seen_tokens = past_seen_tokens - seqlen
-
-        if past_seen_tokens > 0:
-            conv_state = past_key_values.conv_cache[self.layer_idx]
-            positions = torch.arange(seqlen, device=conv_state.device) + past_seen_tokens
-            positions = positions.clamp(0, self.L_cache - 1)
-            conv_state = conv_state.roll(shifts=-1, dims=-1)
-            conv_state[:, :, positions] = Bx.to(device=conv_state.device, dtype=conv_state.dtype)
-            past_key_values.conv_cache[self.layer_idx].copy_(conv_state)
+        if past_key_values is not None and past_key_values.has_previous_state:
+            conv_state = past_key_values.update_conv_state(self.layer_idx, Bx, cache_init=False)
             conv_out = torch.sum(conv_state.to(Bx.device) * self.conv.weight[:, 0, :], dim=-1)
             if self.bias:
                 conv_out += self.conv.bias
@@ -606,7 +607,7 @@ def slow_forward(
         else:
             if past_key_values is not None:
                 conv_state = nn.functional.pad(Bx, (self.L_cache - Bx.shape[-1], 0))
-                past_key_values.conv_cache[self.layer_idx].copy_(conv_state)
+                conv_state = past_key_values.update_conv_state(self.layer_idx, conv_state, cache_init=True)

             conv_out = self.conv(Bx)[..., :seqlen]

PATCH

echo "Patch applied successfully."
