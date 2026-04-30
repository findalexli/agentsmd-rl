#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency check: if contextlib is already removed from modeling_nemotron_h.py, patch is applied
if ! grep -q '^import contextlib' src/transformers/models/nemotron_h/modeling_nemotron_h.py; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/models/nemotron_h/modeling_nemotron_h.py b/src/transformers/models/nemotron_h/modeling_nemotron_h.py
index d0b8fd874449..400431c47427 100644
--- a/src/transformers/models/nemotron_h/modeling_nemotron_h.py
+++ b/src/transformers/models/nemotron_h/modeling_nemotron_h.py
@@ -20,7 +20,6 @@
 # limitations under the License.


-import contextlib
 import math
 from collections.abc import Callable
 from typing import Any
@@ -222,6 +221,9 @@ def segment_sum(input_tensor):
     return tensor_segsum


+is_fast_path_available = False
+
+
 class NemotronHMamba2Mixer(nn.Module):
     """
     Compute ∆, A, B, C, and D the state space parameters and compute the `contextualized_states`.
@@ -677,7 +679,11 @@ def forward(
         **kwargs,
     ):
         if is_fast_path_available and "cuda" in self.in_proj.weight.device.type and not is_torchdynamo_compiling():
-            return self.cuda_kernels_forward(hidden_states, cache_params, attention_mask)
+            # Use cuda stream to avoid NaN when using multiple GPUs, which is caused by multi-GPU synchronization issue.
+            # Mamba might launch on the default cuda stream that not strictly respect the current Pytorch cuda stream.
+            # This leads to kernel reading uninitialized memory before the data transfer is complete.
+            with torch.cuda.stream(torch.cuda.default_stream(hidden_states.device)):
+                return self.cuda_kernels_forward(hidden_states, cache_params, attention_mask)

         return self.torch_forward(hidden_states, cache_params, attention_mask)

@@ -1036,34 +1042,26 @@ def forward(
         use_cache: bool | None = False,
         **kwargs: Unpack[TransformersKwargs],
     ):
-        if hidden_states.device.type == "cuda":
-            # Use cuda stream to avoid NaN when using multiple GPUs, which is caused by multi-GPU synchronization issue.
-            # Mamba might launch on the default cuda stream that not strictly respect the current Pytorch cuda stream.
-            # This leads to kernel reading uninitialized memory before the data transfer is complete.
-            stream_context = torch.cuda.stream(torch.cuda.default_stream(hidden_states.device))
+        residual = hidden_states
+        hidden_states = self.norm(hidden_states.to(dtype=self.norm.weight.dtype))
+
+        if self.block_type == "mamba":
+            hidden_states = self.mixer(hidden_states, cache_params=past_key_values, attention_mask=attention_mask)
+        elif self.block_type == "attention":
+            hidden_states, _ = self.mixer(
+                hidden_states=hidden_states,
+                past_key_values=past_key_values,
+                attention_mask=attention_mask,
+                position_ids=position_ids,
+                user_cache=use_cache,
+                **kwargs,
+            )
         else:
-            stream_context = contextlib.nullcontext()
-
-        with stream_context:
-            residual = hidden_states
-            hidden_states = self.norm(hidden_states.to(dtype=self.norm.weight.dtype))
-
-            if self.block_type == "mamba":
-                hidden_states = self.mixer(hidden_states, cache_params=past_key_values, attention_mask=attention_mask)
-            elif self.block_type == "attention":
-                hidden_states, _ = self.mixer(
-                    hidden_states=hidden_states,
-                    past_key_values=past_key_values,
-                    attention_mask=attention_mask,
-                    position_ids=position_ids,
-                    user_cache=use_cache,
-                    **kwargs,
-                )
-            else:
-                hidden_states = self.mixer(hidden_states)
+            hidden_states = self.mixer(hidden_states)

-            hidden_states = residual + hidden_states
-            return hidden_states
+        hidden_states = residual + hidden_states
+
+        return hidden_states


 class NemotronHPreTrainedModel(PreTrainedModel):
diff --git a/src/transformers/models/nemotron_h/modular_nemotron_h.py b/src/transformers/models/nemotron_h/modular_nemotron_h.py
index ab9f24718c00..6ca29710ebb2 100644
--- a/src/transformers/models/nemotron_h/modular_nemotron_h.py
+++ b/src/transformers/models/nemotron_h/modular_nemotron_h.py
@@ -15,7 +15,6 @@

 from __future__ import annotations

-import contextlib
 import math

 import torch
@@ -35,7 +34,7 @@
 from ...models.zamba.modeling_zamba import ZambaForCausalLM
 from ...models.zamba2.modeling_zamba2 import Zamba2HybridDynamicCache, Zamba2MambaMixer, Zamba2RMSNormGated
 from ...processing_utils import Unpack
-from ...utils import TransformersKwargs, auto_docstring, can_return_tuple, logging
+from ...utils import TransformersKwargs, auto_docstring, can_return_tuple, is_torchdynamo_compiling, logging
 from ...utils.generic import merge_with_config_defaults
 from ...utils.output_capturing import capture_outputs
 from .configuration_nemotron_h import NemotronHConfig
@@ -43,6 +42,8 @@

 logger = logging.get_logger(__name__)

+is_fast_path_available = False
+

 class NemotronHHybridDynamicCache(Zamba2HybridDynamicCache):
     def __init__(
@@ -129,6 +130,22 @@ def __init__(self, config: NemotronHConfig, layer_idx: int | None = None):

         self.out_proj = nn.Linear(self.intermediate_size, self.hidden_size, bias=config.use_bias)

+    def forward(
+        self,
+        hidden_states,
+        cache_params: NemotronHHybridDynamicCache | None = None,
+        attention_mask: torch.Tensor | None = None,
+        **kwargs,
+    ):
+        if is_fast_path_available and "cuda" in self.in_proj.weight.device.type and not is_torchdynamo_compiling():
+            # Use cuda stream to avoid NaN when using multiple GPUs, which is caused by multi-GPU synchronization issue.
+            # Mamba might launch on the default cuda stream that not strictly respect the current Pytorch cuda stream.
+            # This leads to kernel reading uninitialized memory before the data transfer is complete.
+            with torch.cuda.stream(torch.cuda.default_stream(hidden_states.device)):
+                return self.cuda_kernels_forward(hidden_states, cache_params, attention_mask)
+
+        return self.torch_forward(hidden_states, cache_params, attention_mask)
+

 class NemotronHRMSNorm(LlamaRMSNorm):
     pass
@@ -307,34 +324,26 @@ def forward(
         use_cache: bool | None = False,
         **kwargs: Unpack[TransformersKwargs],
     ):
-        if hidden_states.device.type == "cuda":
-            # Use cuda stream to avoid NaN when using multiple GPUs, which is caused by multi-GPU synchronization issue.
-            # Mamba might launch on the default cuda stream that not strictly respect the current Pytorch cuda stream.
-            # This leads to kernel reading uninitialized memory before the data transfer is complete.
-            stream_context = torch.cuda.stream(torch.cuda.default_stream(hidden_states.device))
+        residual = hidden_states
+        hidden_states = self.norm(hidden_states.to(dtype=self.norm.weight.dtype))
+
+        if self.block_type == "mamba":
+            hidden_states = self.mixer(hidden_states, cache_params=past_key_values, attention_mask=attention_mask)
+        elif self.block_type == "attention":
+            hidden_states, _ = self.mixer(
+                hidden_states=hidden_states,
+                past_key_values=past_key_values,
+                attention_mask=attention_mask,
+                position_ids=position_ids,
+                user_cache=use_cache,
+                **kwargs,
+            )
         else:
-            stream_context = contextlib.nullcontext()
-
-        with stream_context:
-            residual = hidden_states
-            hidden_states = self.norm(hidden_states.to(dtype=self.norm.weight.dtype))
-
-            if self.block_type == "mamba":
-                hidden_states = self.mixer(hidden_states, cache_params=past_key_values, attention_mask=attention_mask)
-            elif self.block_type == "attention":
-                hidden_states, _ = self.mixer(
-                    hidden_states=hidden_states,
-                    past_key_values=past_key_values,
-                    attention_mask=attention_mask,
-                    position_ids=position_ids,
-                    user_cache=use_cache,
-                    **kwargs,
-                )
-            else:
-                hidden_states = self.mixer(hidden_states)
+            hidden_states = self.mixer(hidden_states)

-            hidden_states = residual + hidden_states
-            return hidden_states
+        hidden_states = residual + hidden_states
+
+        return hidden_states


 class NemotronHPreTrainedModel(PreTrainedModel):

PATCH

echo "Patch applied successfully."
