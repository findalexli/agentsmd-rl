#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotent: skip if already applied (check for distinctive line from fix)
if grep -q 'q_input_shape = (batch_size, seq_length, -1, self.key_value_proj_dim)' src/transformers/models/t5/modeling_t5.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/src/transformers/models/t5/modeling_t5.py b/src/transformers/models/t5/modeling_t5.py
index c828c8bc8e31..8deaf51ad77e 100644
--- a/src/transformers/models/t5/modeling_t5.py
+++ b/src/transformers/models/t5/modeling_t5.py
@@ -273,8 +273,8 @@ class T5Attention(nn.Module):
         # if key_value_states are provided this layer is used as a cross-attention layer for the decoder
         is_cross_attention = key_value_states is not None

-        query_states = self.q(hidden_states)
-        query_states = query_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
+        q_input_shape = (batch_size, seq_length, -1, self.key_value_proj_dim)
+        query_states = self.q(hidden_states).view(*q_input_shape).transpose(1, 2)

         # Check is encoder-decoder model is being used. Otherwise we'll get `DynamicCache`
         is_updated = False
@@ -294,10 +294,9 @@ class T5Attention(nn.Module):
             key_states = curr_past_key_values.layers[self.layer_idx].keys
             value_states = curr_past_key_values.layers[self.layer_idx].values
         else:
-            key_states = self.k(current_states)
-            value_states = self.v(current_states)
-            key_states = key_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
-            value_states = value_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
+            kv_input_shape = (batch_size, current_states.shape[1], -1, self.key_value_proj_dim)
+            key_states = self.k(current_states).view(*kv_input_shape).transpose(1, 2)
+            value_states = self.v(current_states).view(*kv_input_shape).transpose(1, 2)

             if past_key_values is not None:
                 key_states, value_states = curr_past_key_values.update(key_states, value_states, self.layer_idx)
@@ -312,7 +311,7 @@ class T5Attention(nn.Module):
             key_length = key_states.shape[-2]
             if not self.has_relative_attention_bias:
                 position_bias = torch.zeros(
-                    (1, self.n_heads, seq_length, key_length), device=scores.device, dtype=scores.dtype
+                    (1, query_states.shape[1], seq_length, key_length), device=scores.device, dtype=scores.dtype
                 )
                 if self.gradient_checkpointing and self.training:
                     position_bias.requires_grad = True
@@ -335,7 +334,7 @@ class T5Attention(nn.Module):
         attn_output = torch.matmul(attn_weights, value_states)

         attn_output = attn_output.transpose(1, 2).contiguous()
-        attn_output = attn_output.view(batch_size, -1, self.inner_dim)
+        attn_output = attn_output.view(batch_size, seq_length, -1)
         attn_output = self.o(attn_output)

         outputs = (attn_output, position_bias)

diff --git a/src/transformers/models/mt5/modeling_mt5.py b/src/transformers/models/mt5/modeling_mt5.py
index 58ee53fa1039..90a9515397bb 100644
--- a/src/transformers/models/mt5/modeling_mt5.py
+++ b/src/transformers/models/mt5/modeling_mt5.py
@@ -265,8 +265,8 @@ class MT5Attention(nn.Module):
         # if key_value_states are provided this layer is used as a cross-attention layer for the decoder
         is_cross_attention = key_value_states is not None

-        query_states = self.q(hidden_states)
-        query_states = query_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
+        q_input_shape = (batch_size, seq_length, -1, self.key_value_proj_dim)
+        query_states = self.q(hidden_states).view(*q_input_shape).transpose(1, 2)

         # Check is encoder-decoder model is being used. Otherwise we'll get `DynamicCache`
         is_updated = False
@@ -286,10 +286,9 @@ class MT5Attention(nn.Module):
             key_states = curr_past_key_values.layers[self.layer_idx].keys
             value_states = curr_past_key_values.layers[self.layer_idx].values
         else:
-            key_states = self.k(current_states)
-            value_states = self.v(current_states)
-            key_states = key_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
-            value_states = value_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
+            kv_input_shape = (batch_size, current_states.shape[1], -1, self.key_value_proj_dim)
+            key_states = self.k(current_states).view(*kv_input_shape).transpose(1, 2)
+            value_states = self.v(current_states).view(*kv_input_shape).transpose(1, 2)

             if past_key_values is not None:
                 key_states, value_states = curr_past_key_values.update(key_states, value_states, self.layer_idx)
@@ -304,7 +303,7 @@ class MT5Attention(nn.Module):
             key_length = key_states.shape[-2]
             if not self.has_relative_attention_bias:
                 position_bias = torch.zeros(
-                    (1, self.n_heads, seq_length, key_length), device=scores.device, dtype=scores.dtype
+                    (1, query_states.shape[1], seq_length, key_length), device=scores.device, dtype=scores.dtype
                 )
                 if self.gradient_checkpointing and self.training:
                     position_bias.requires_grad = True
@@ -327,7 +326,7 @@ class MT5Attention(nn.Module):
         attn_output = torch.matmul(attn_weights, value_states)

         attn_output = attn_output.transpose(1, 2).contiguous()
-        attn_output = attn_output.view(batch_size, -1, self.inner_dim)
+        attn_output = attn_output.view(batch_size, seq_length, -1)
         attn_output = self.o(attn_output)

         outputs = (attn_output, position_bias)

diff --git a/src/transformers/models/longt5/modeling_longt5.py b/src/transformers/models/longt5/modeling_longt5.py
index b178e50dc352..16a90e89cc77 100644
--- a/src/transformers/models/longt5/modeling_longt5.py
+++ b/src/transformers/models/longt5/modeling_longt5.py
@@ -433,8 +433,8 @@ class LongT5Attention(nn.Module):
         # if key_value_states are provided this layer is used as a cross-attention layer for the decoder
         is_cross_attention = key_value_states is not None

-        query_states = self.q(hidden_states)
-        query_states = query_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
+        q_input_shape = (batch_size, seq_length, -1, self.key_value_proj_dim)
+        query_states = self.q(hidden_states).view(*q_input_shape).transpose(1, 2)

         # Check is encoder-decoder model is being used. Otherwise we'll get `DynamicCache`
         is_updated = False
@@ -454,10 +454,9 @@ class LongT5Attention(nn.Module):
             key_states = curr_past_key_values.layers[self.layer_idx].keys
             value_states = curr_past_key_values.layers[self.layer_idx].values
         else:
-            key_states = self.k(current_states)
-            value_states = self.v(current_states)
-            key_states = key_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
-            value_states = value_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
+            kv_input_shape = (batch_size, current_states.shape[1], -1, self.key_value_proj_dim)
+            key_states = self.k(current_states).view(*kv_input_shape).transpose(1, 2)
+            value_states = self.v(current_states).view(*kv_input_shape).transpose(1, 2)

             if past_key_values is not None:
                 key_states, value_states = curr_past_key_values.update(key_states, value_states, self.layer_idx)
@@ -472,7 +471,7 @@ class LongT5Attention(nn.Module):
             key_length = key_states.shape[-2]
             if not self.has_relative_attention_bias:
                 position_bias = torch.zeros(
-                    (1, self.n_heads, seq_length, key_length), device=scores.device, dtype=scores.dtype
+                    (1, query_states.shape[1], seq_length, key_length), device=scores.device, dtype=scores.dtype
                 )
                 if self.gradient_checkpointing and self.training:
                     position_bias.requires_grad = True
@@ -495,7 +494,7 @@ class LongT5Attention(nn.Module):
         attn_output = torch.matmul(attn_weights, value_states)

         attn_output = attn_output.transpose(1, 2).contiguous()
-        attn_output = attn_output.view(batch_size, -1, self.inner_dim)
+        attn_output = attn_output.view(batch_size, seq_length, -1)
         attn_output = self.o(attn_output)

         outputs = (attn_output, position_bias)

diff --git a/src/transformers/models/udop/modeling_udop.py b/src/transformers/models/udop/modeling_udop.py
index d9186136b555..3cf52f9b2f6a 100644
--- a/src/transformers/models/udop/modeling_udop.py
+++ b/src/transformers/models/udop/modeling_udop.py
@@ -551,8 +551,8 @@ class UdopAttention(nn.Module):
         # if key_value_states are provided this layer is used as a cross-attention layer for the decoder
         is_cross_attention = key_value_states is not None

-        query_states = self.q(hidden_states)
-        query_states = query_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
+        q_input_shape = (batch_size, seq_length, -1, self.key_value_proj_dim)
+        query_states = self.q(hidden_states).view(*q_input_shape).transpose(1, 2)

         # Check is encoder-decoder model is being used. Otherwise we'll get `DynamicCache`
         is_updated = False
@@ -572,10 +572,9 @@ class UdopAttention(nn.Module):
             key_states = curr_past_key_values.layers[self.layer_idx].keys
             value_states = curr_past_key_values.layers[self.layer_idx].values
         else:
-            key_states = self.k(current_states)
-            value_states = self.v(current_states)
-            key_states = key_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
-            value_states = value_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
+            kv_input_shape = (batch_size, current_states.shape[1], -1, self.key_value_proj_dim)
+            key_states = self.k(current_states).view(*kv_input_shape).transpose(1, 2)
+            value_states = self.v(current_states).view(*kv_input_shape).transpose(1, 2)

             if past_key_values is not None:
                 key_states, value_states = curr_past_key_values.update(key_states, value_states, self.layer_idx)
@@ -590,7 +589,7 @@ class UdopAttention(nn.Module):
             key_length = key_states.shape[-2]
             if not self.has_relative_attention_bias:
                 position_bias = torch.zeros(
-                    (1, self.n_heads, seq_length, key_length), device=scores.device, dtype=scores.dtype
+                    (1, query_states.shape[1], seq_length, key_length), device=scores.device, dtype=scores.dtype
                 )
                 if self.gradient_checkpointing and self.training:
                     position_bias.requires_grad = True
@@ -613,7 +612,7 @@ class UdopAttention(nn.Module):
         attn_output = torch.matmul(attn_weights, value_states)

         attn_output = attn_output.transpose(1, 2).contiguous()
-        attn_output = attn_output.view(batch_size, -1, self.inner_dim)
+        attn_output = attn_output.view(batch_size, seq_length, -1)
         attn_output = self.o(attn_output)

         outputs = (attn_output, position_bias)

diff --git a/src/transformers/models/pop2piano/modeling_pop2piano.py b/src/transformers/models/pop2piano/modeling_pop2piano.py
index 08595168ab01..852e60c136a6 100644
--- a/src/transformers/models/pop2piano/modeling_pop2piano.py
+++ b/src/transformers/models/pop2piano/modeling_pop2piano.py
@@ -277,8 +277,8 @@ class Pop2PianoAttention(nn.Module):
         # if key_value_states are provided this layer is used as a cross-attention layer for the decoder
         is_cross_attention = key_value_states is not None

-        query_states = self.q(hidden_states)
-        query_states = query_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
+        q_input_shape = (batch_size, seq_length, -1, self.key_value_proj_dim)
+        query_states = self.q(hidden_states).view(*q_input_shape).transpose(1, 2)

         # Check is encoder-decoder model is being used. Otherwise we'll get `DynamicCache`
         is_updated = False
@@ -298,10 +298,9 @@ class Pop2PianoAttention(nn.Module):
             key_states = curr_past_key_values.layers[self.layer_idx].keys
             value_states = curr_past_key_values.layers[self.layer_idx].values
         else:
-            key_states = self.k(current_states)
-            value_states = self.v(current_states)
-            key_states = key_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
-            value_states = value_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
+            kv_input_shape = (batch_size, current_states.shape[1], -1, self.key_value_proj_dim)
+            key_states = self.k(current_states).view(*kv_input_shape).transpose(1, 2)
+            value_states = self.v(current_states).view(*kv_input_shape).transpose(1, 2)

             if past_key_values is not None:
                 key_states, value_states = curr_past_key_values.update(key_states, value_states, self.layer_idx)
@@ -316,7 +315,7 @@ class Pop2PianoAttention(nn.Module):
             key_length = key_states.shape[-2]
             if not self.has_relative_attention_bias:
                 position_bias = torch.zeros(
-                    (1, self.n_heads, seq_length, key_length), device=scores.device, dtype=scores.dtype
+                    (1, query_states.shape[1], seq_length, key_length), device=scores.device, dtype=scores.dtype
                 )
                 if self.gradient_checkpointing and self.training:
                     position_bias.requires_grad = True
@@ -339,7 +338,7 @@ class Pop2PianoAttention(nn.Module):
         attn_output = torch.matmul(attn_weights, value_states)

         attn_output = attn_output.transpose(1, 2).contiguous()
-        attn_output = attn_output.view(batch_size, -1, self.inner_dim)
+        attn_output = attn_output.view(batch_size, seq_length, -1)
         attn_output = self.o(attn_output)

         outputs = (attn_output, position_bias)

diff --git a/src/transformers/models/switch_transformers/modeling_switch_transformers.py b/src/transformers/models/switch_transformers/modeling_switch_transformers.py
index 262825fe9ea4..54eb8b96f4a8 100644
--- a/src/transformers/models/switch_transformers/modeling_switch_transformers.py
+++ b/src/transformers/models/switch_transformers/modeling_switch_transformers.py
@@ -344,8 +344,8 @@ class SwitchTransformersAttention(nn.Module):
         # if key_value_states are provided this layer is used as a cross-attention layer for the decoder
         is_cross_attention = key_value_states is not None

-        query_states = self.q(hidden_states)
-        query_states = query_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
+        q_input_shape = (batch_size, seq_length, -1, self.key_value_proj_dim)
+        query_states = self.q(hidden_states).view(*q_input_shape).transpose(1, 2)

         # Check is encoder-decoder model is being used. Otherwise we'll get `DynamicCache`
         is_updated = False
@@ -365,10 +365,9 @@ class SwitchTransformersAttention(nn.Module):
             key_states = curr_past_key_values.layers[self.layer_idx].keys
             value_states = curr_past_key_values.layers[self.layer_idx].values
         else:
-            key_states = self.k(current_states)
-            value_states = self.v(current_states)
-            key_states = key_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
-            value_states = value_states.view(batch_size, -1, self.n_heads, self.key_value_proj_dim).transpose(1, 2)
+            kv_input_shape = (batch_size, current_states.shape[1], -1, self.key_value_proj_dim)
+            key_states = self.k(current_states).view(*kv_input_shape).transpose(1, 2)
+            value_states = self.v(current_states).view(*kv_input_shape).transpose(1, 2)

             if past_key_values is not None:
                 key_states, value_states = curr_past_key_values.update(key_states, value_states, self.layer_idx)
@@ -383,7 +382,7 @@ class SwitchTransformersAttention(nn.Module):
             key_length = key_states.shape[-2]
             if not self.has_relative_attention_bias:
                 position_bias = torch.zeros(
-                    (1, self.n_heads, seq_length, key_length), device=scores.device, dtype=scores.dtype
+                    (1, query_states.shape[1], seq_length, key_length), device=scores.device, dtype=scores.dtype
                 )
                 if self.gradient_checkpointing and self.training:
                     position_bias.requires_grad = True
@@ -406,7 +405,7 @@ class SwitchTransformersAttention(nn.Module):
         attn_output = torch.matmul(attn_weights, value_states)

         attn_output = attn_output.transpose(1, 2).contiguous()
-        attn_output = attn_output.view(batch_size, -1, self.inner_dim)
+        attn_output = attn_output.view(batch_size, seq_length, -1)
         attn_output = self.o(attn_output)

         outputs = (attn_output, position_bias)

PATCH

echo "Patch applied successfully."
