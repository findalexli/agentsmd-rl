#!/usr/bin/env bash
# Gold solution: apply the upstream fix from PR huggingface/transformers#45564.
# The patch removes the @use_kernelized_func(apply_rotary_pos_emb) decorator
# from Gemma3nTextAttention and Gemma4TextAttention (in both modular and
# modeling files), and drops the now-unused import.

set -euo pipefail

cd /workspace/transformers

# Idempotency guard: the distinctive line is the decorator on Gemma3nTextAttention
# in the modeling file. If it's already gone, the patch has been applied.
if ! grep -q "^@use_kernelized_func(apply_rotary_pos_emb)$" src/transformers/models/gemma3n/modeling_gemma3n.py; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/transformers/models/gemma3n/modeling_gemma3n.py b/src/transformers/models/gemma3n/modeling_gemma3n.py
index 3c07556708b0..dab9c5dbb4fa 100644
--- a/src/transformers/models/gemma3n/modeling_gemma3n.py
+++ b/src/transformers/models/gemma3n/modeling_gemma3n.py
@@ -31,7 +31,6 @@
 from ...activations import ACT2FN
 from ...cache_utils import Cache, DynamicCache
 from ...generation import GenerationMixin
-from ...integrations import use_kernelized_func
 from ...masking_utils import create_causal_mask, create_sliding_window_causal_mask
 from ...modeling_layers import GradientCheckpointingLayer
 from ...modeling_outputs import BaseModelOutputWithPast, BaseModelOutputWithPooling, CausalLMOutputWithPast
@@ -1168,7 +1167,6 @@ def apply_rotary_pos_emb(x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor,
     return (x * cos) + (rotate_half(x) * sin)


-@use_kernelized_func(apply_rotary_pos_emb)
 class Gemma3nTextAttention(nn.Module):
     def __init__(self, config: Gemma3nTextConfig, layer_idx: int):
         super().__init__()
diff --git a/src/transformers/models/gemma3n/modular_gemma3n.py b/src/transformers/models/gemma3n/modular_gemma3n.py
index 356baa483b10..df9d65d5ec3c 100644
--- a/src/transformers/models/gemma3n/modular_gemma3n.py
+++ b/src/transformers/models/gemma3n/modular_gemma3n.py
@@ -26,7 +26,6 @@
 from ...activations import ACT2FN
 from ...cache_utils import Cache, DynamicCache
 from ...configuration_utils import PreTrainedConfig
-from ...integrations import use_kernelized_func
 from ...masking_utils import create_causal_mask, create_sliding_window_causal_mask
 from ...modeling_outputs import BaseModelOutputWithPast, BaseModelOutputWithPooling
 from ...modeling_rope_utils import ROPE_INIT_FUNCTIONS
@@ -1463,7 +1462,6 @@ def apply_rotary_pos_emb(x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor,
     return (x * cos) + (rotate_half(x) * sin)


-@use_kernelized_func(apply_rotary_pos_emb)
 class Gemma3nTextAttention(nn.Module):
     def __init__(self, config: Gemma3nTextConfig, layer_idx: int):
         super().__init__()
diff --git a/src/transformers/models/gemma4/modeling_gemma4.py b/src/transformers/models/gemma4/modeling_gemma4.py
index 5b147f95ba36..4ea3eac7b550 100644
--- a/src/transformers/models/gemma4/modeling_gemma4.py
+++ b/src/transformers/models/gemma4/modeling_gemma4.py
@@ -1133,7 +1133,6 @@ def forward(self, x, position_ids, layer_type=None):
         return cos.to(dtype=x.dtype), sin.to(dtype=x.dtype)


-@use_kernelized_func(apply_rotary_pos_emb)
 class Gemma4TextAttention(nn.Module):
     """Multi-headed attention from 'Attention Is All You Need' paper"""

diff --git a/src/transformers/models/gemma4/modular_gemma4.py b/src/transformers/models/gemma4/modular_gemma4.py
index 12412b319b5c..8feb4129525c 100644
--- a/src/transformers/models/gemma4/modular_gemma4.py
+++ b/src/transformers/models/gemma4/modular_gemma4.py
@@ -25,7 +25,6 @@
 from ...activations import ACT2FN
 from ...cache_utils import Cache, DynamicCache
 from ...configuration_utils import PreTrainedConfig
-from ...integrations import use_kernelized_func
 from ...masking_utils import (
     create_bidirectional_mask,
     create_causal_mask,
@@ -901,7 +900,6 @@ def __init__(self, config: Gemma4TextConfig, device=None, layer_type=None):
             setattr(self, f"{layer_type}_attention_scaling", curr_attention_scaling)


-@use_kernelized_func(apply_rotary_pos_emb)
 class Gemma4TextAttention(nn.Module):
     """Multi-headed attention from 'Attention Is All You Need' paper"""

PATCH

echo "Patch applied successfully."
