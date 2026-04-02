#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency check: if fix is already applied, the scaling line uses [:, None, :, None]
if grep -q 'scaling\[:, None, :, None\]' src/transformers/models/ministral3/modular_ministral3.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/models/ministral3/modeling_ministral3.py b/src/transformers/models/ministral3/modeling_ministral3.py
index 6e76c94e90ab..6aacf4c8ce3a 100644
--- a/src/transformers/models/ministral3/modeling_ministral3.py
+++ b/src/transformers/models/ministral3/modeling_ministral3.py
@@ -104,7 +104,7 @@ def eager_attention_forward(

 def get_llama_4_attn_scale(positions_ids: torch.Tensor, beta: float, max_position_embeddings: int) -> torch.Tensor:
     scaling = 1 + beta * torch.log(1 + torch.floor(positions_ids / max_position_embeddings))
-    return scaling.unsqueeze(-1)
+    return scaling[:, None, :, None]


 @use_kernelized_func(apply_rotary_pos_emb)
@@ -130,6 +130,7 @@ def forward(
         hidden_states: torch.Tensor,
         position_embeddings: tuple[torch.Tensor, torch.Tensor],
         attention_mask: torch.Tensor | None,
+        position_ids: torch.Tensor,
         past_key_values: Cache | None = None,
         **kwargs: Unpack[FlashAttentionKwargs],
     ) -> tuple[torch.Tensor, torch.Tensor | None]:
@@ -142,10 +143,8 @@ def forward(

         cos, sin = position_embeddings
         query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
-        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
-        absolute_positions = torch.arange(query_states.shape[2], device=query_states.device) + past_seen_tokens
         query_states = query_states * get_llama_4_attn_scale(
-            absolute_positions,
+            position_ids,
             self.config.rope_parameters.get("llama_4_scaling_beta"),
             self.config.rope_parameters.get("original_max_position_embeddings"),
         ).to(query_states.dtype)
diff --git a/src/transformers/models/ministral3/modular_ministral3.py b/src/transformers/models/ministral3/modular_ministral3.py
index 25c0d763c157..0a925f5d404d 100644
--- a/src/transformers/models/ministral3/modular_ministral3.py
+++ b/src/transformers/models/ministral3/modular_ministral3.py
@@ -28,7 +28,7 @@

 def get_llama_4_attn_scale(positions_ids: torch.Tensor, beta: float, max_position_embeddings: int) -> torch.Tensor:
     scaling = 1 + beta * torch.log(1 + torch.floor(positions_ids / max_position_embeddings))
-    return scaling.unsqueeze(-1)
+    return scaling[:, None, :, None]


 class Ministral3Attention(MistralAttention):
@@ -37,6 +37,7 @@ def forward(
         hidden_states: torch.Tensor,
         position_embeddings: tuple[torch.Tensor, torch.Tensor],
         attention_mask: torch.Tensor | None,
+        position_ids: torch.Tensor,
         past_key_values: Cache | None = None,
         **kwargs: Unpack[FlashAttentionKwargs],
     ) -> tuple[torch.Tensor, torch.Tensor | None]:
@@ -49,10 +50,8 @@ def forward(

         cos, sin = position_embeddings
         query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
-        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
-        absolute_positions = torch.arange(query_states.shape[2], device=query_states.device) + past_seen_tokens
         query_states = query_states * get_llama_4_attn_scale(
-            absolute_positions,
+            position_ids,
             self.config.rope_parameters.get("llama_4_scaling_beta"),
             self.config.rope_parameters.get("original_max_position_embeddings"),
         ).to(query_states.dtype)
diff --git a/src/transformers/models/mistral4/modeling_mistral4.py b/src/transformers/models/mistral4/modeling_mistral4.py
index ea71af247f97..006ddad187bf 100644
--- a/src/transformers/models/mistral4/modeling_mistral4.py
+++ b/src/transformers/models/mistral4/modeling_mistral4.py
@@ -365,7 +365,7 @@ def apply_rotary_pos_emb_interleave(q, k, cos, sin, position_ids=None, unsqueeze

 def get_llama_4_attn_scale(positions_ids: torch.Tensor, beta: float, max_position_embeddings: int) -> torch.Tensor:
     scaling = 1 + beta * torch.log(1 + torch.floor(positions_ids / max_position_embeddings))
-    return scaling.unsqueeze(-1)
+    return scaling[:, None, :, None]


 class Mistral4Attention(nn.Module):
@@ -419,6 +419,7 @@ def forward(
         hidden_states: torch.Tensor,
         position_embeddings: tuple[torch.Tensor, torch.Tensor],
         attention_mask: torch.Tensor | None,
+        position_ids: torch.Tensor,
         past_key_values: Cache | None = None,
         **kwargs: Unpack[FlashAttentionKwargs],
     ) -> tuple[torch.Tensor, torch.Tensor | None, tuple[torch.Tensor] | None]:
@@ -451,11 +452,8 @@ def forward(
         query_states = torch.cat((q_pass, q_rot), dim=-1)
         key_states = torch.cat((k_pass, k_rot), dim=-1)

-        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
-        absolute_positions = torch.arange(query_states.shape[2], device=query_states.device) + past_seen_tokens
-
         query_states = query_states * get_llama_4_attn_scale(
-            absolute_positions,
+            position_ids,
             self.config.rope_parameters.get("llama_4_scaling_beta"),
             self.config.rope_parameters.get("original_max_position_embeddings"),
         ).to(query_states.dtype)
diff --git a/src/transformers/models/mistral4/modular_mistral4.py b/src/transformers/models/mistral4/modular_mistral4.py
index 77d6bcc7d6c3..acd9f1f60191 100644
--- a/src/transformers/models/mistral4/modular_mistral4.py
+++ b/src/transformers/models/mistral4/modular_mistral4.py
@@ -151,6 +151,7 @@ def forward(
         hidden_states: torch.Tensor,
         position_embeddings: tuple[torch.Tensor, torch.Tensor],
         attention_mask: torch.Tensor | None,
+        position_ids: torch.Tensor,
         past_key_values: Cache | None = None,
         **kwargs: Unpack[FlashAttentionKwargs],
     ) -> tuple[torch.Tensor, torch.Tensor | None, tuple[torch.Tensor] | None]:
@@ -183,11 +184,8 @@ def forward(
         query_states = torch.cat((q_pass, q_rot), dim=-1)
         key_states = torch.cat((k_pass, k_rot), dim=-1)

-        past_seen_tokens = past_key_values.get_seq_length() if past_key_values is not None else 0
-        absolute_positions = torch.arange(query_states.shape[2], device=query_states.device) + past_seen_tokens
-
         query_states = query_states * get_llama_4_attn_scale(
-            absolute_positions,
+            position_ids,
             self.config.rope_parameters.get("llama_4_scaling_beta"),
             self.config.rope_parameters.get("original_max_position_embeddings"),
         ).to(query_states.dtype)

PATCH

echo "Patch applied successfully."
