#!/bin/bash
set -euo pipefail

cd /workspace/transformers

# Idempotency: skip if gold patch already applied (modernbert files had 0 get_interface on base)
if grep -q 'ALL_ATTENTION_FUNCTIONS.get_interface(' \
    src/transformers/models/modernbert/modeling_modernbert.py; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
git apply <<'PATCH'
diff --git a/src/transformers/models/gemma4/modeling_gemma4.py b/src/transformers/models/gemma4/modeling_gemma4.py
--- a/src/transformers/models/gemma4/modeling_gemma4.py
+++ b/src/transformers/models/gemma4/modeling_gemma4.py
@@ -1235,9 +1235,9 @@ def forward(
         if self.store_full_length_kv:
             shared_kv_states[self.layer_idx] = key_states, value_states

-        attention_interface: Callable = eager_attention_forward
-        if self.config._attn_implementation != "eager":
-            attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
+        attention_interface: Callable = ALL_ATTENTION_FUNCTIONS.get_interface(
+            self.config._attn_implementation, eager_attention_forward
+        )

         attn_output, attn_weights = attention_interface(
             self,
diff --git a/src/transformers/models/gemma4/modular_gemma4.py b/src/transformers/models/gemma4/modular_gemma4.py
--- a/src/transformers/models/gemma4/modular_gemma4.py
+++ b/src/transformers/models/gemma4/modular_gemma4.py
@@ -1002,9 +1002,9 @@ def forward(
         if self.store_full_length_kv:
             shared_kv_states[self.layer_idx] = key_states, value_states

-        attention_interface: Callable = eager_attention_forward
-        if self.config._attn_implementation != "eager":
-            attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
+        attention_interface: Callable = ALL_ATTENTION_FUNCTIONS.get_interface(
+            self.config._attn_implementation, eager_attention_forward
+        )

         attn_output, attn_weights = attention_interface(
             self,
diff --git a/src/transformers/models/modernbert/modeling_modernbert.py b/src/transformers/models/modernbert/modeling_modernbert.py
--- a/src/transformers/models/modernbert/modeling_modernbert.py
+++ b/src/transformers/models/modernbert/modeling_modernbert.py
@@ -288,9 +288,9 @@ def forward(
         cos, sin = position_embeddings
         query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin, unsqueeze_dim=1)

-        attention_interface = eager_attention_forward
-        if self.config._attn_implementation != "eager":
-            attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
+        attention_interface: Callable = ALL_ATTENTION_FUNCTIONS.get_interface(
+            self.config._attn_implementation, eager_attention_forward
+        )

         attn_output, attn_weights = attention_interface(
             self,
diff --git a/src/transformers/models/modernbert/modular_modernbert.py b/src/transformers/models/modernbert/modular_modernbert.py
--- a/src/transformers/models/modernbert/modular_modernbert.py
+++ b/src/transformers/models/modernbert/modular_modernbert.py
@@ -14,6 +14,7 @@
 # limitations under the License.

 import math
+from collections.abc import Callable
 from typing import Literal, Optional

 import torch
@@ -331,9 +332,9 @@ def forward(
         cos, sin = position_embeddings
         query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin, unsqueeze_dim=1)

-        attention_interface = eager_attention_forward
-        if self.config._attn_implementation != "eager":
-            attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
+        attention_interface: Callable = ALL_ATTENTION_FUNCTIONS.get_interface(
+            self.config._attn_implementation, eager_attention_forward
+        )

         attn_output, attn_weights = attention_interface(
             self,
diff --git a/src/transformers/models/moonshine_streaming/modeling_moonshine_streaming.py b/src/transformers/models/moonshine_streaming/modeling_moonshine_streaming.py
--- a/src/transformers/models/moonshine_streaming/modeling_moonshine_streaming.py
+++ b/src/transformers/models/moonshine_streaming/modeling_moonshine_streaming.py
@@ -211,9 +211,9 @@ def forward(
         key_states = self.k_proj(hidden_states).view(hidden_shape).transpose(1, 2)
         value_states = self.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)

-        attention_interface: Callable = eager_attention_forward
-        if self.config._attn_implementation != "eager":
-            attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
+        attention_interface: Callable = ALL_ATTENTION_FUNCTIONS.get_interface(
+            self.config._attn_implementation, eager_attention_forward
+        )

         attn_output, attn_weights = attention_interface(
             self,
diff --git a/src/transformers/models/moonshine_streaming/modular_moonshine_streaming.py b/src/transformers/models/moonshine_streaming/modular_moonshine_streaming.py
--- a/src/transformers/models/moonshine_streaming/modular_moonshine_streaming.py
+++ b/src/transformers/models/moonshine_streaming/modular_moonshine_streaming.py
@@ -172,9 +172,9 @@ def forward(
         key_states = self.k_proj(hidden_states).view(hidden_shape).transpose(1, 2)
         value_states = self.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)

-        attention_interface: Callable = eager_attention_forward
-        if self.config._attn_implementation != "eager":
-            attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
+        attention_interface: Callable = ALL_ATTENTION_FUNCTIONS.get_interface(
+            self.config._attn_implementation, eager_attention_forward
+        )

         attn_output, attn_weights = attention_interface(
             self,
PATCH
