#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

TARGET="docker/patch/latest/sglang.patch"

# Idempotency check: if fix is already applied, exit
if grep -q 'should_fuse_mlp_allreduce_with_next_layer' "$TARGET" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'PYEOF'
import re, sys

target = "docker/patch/latest/sglang.patch"
content = open(target).read()

# Split into diff sections
sections = re.split(r'(?=^diff --git )', content, flags=re.MULTILINE)

found = False
for i, s in enumerate(sections):
    if 'qwen3_5.py' not in s.split('\n', 1)[0]:
        continue
    found = True

    # Build the replacement section
    new_section = """\
diff --git a/python/sglang/srt/models/qwen3_5.py b/python/sglang/srt/models/qwen3_5.py
index f012254..1dad8bb 100644
--- a/python/sglang/srt/models/qwen3_5.py
+++ b/python/sglang/srt/models/qwen3_5.py
@@ -372,6 +372,8 @@ class Qwen3_5LinearDecoderLayer(nn.Module):
             input_layernorm=self.input_layernorm,
             post_attention_layernorm=self.post_attention_layernorm,
             allow_reduce_scatter=True,
+            allow_allreduce_fusion=True,
+            is_last_layer=(layer_id == config.num_hidden_layers - 1),
         )

     def forward(
@@ -400,11 +402,24 @@ class Qwen3_5LinearDecoderLayer(nn.Module):
         use_reduce_scatter = self.layer_communicator.should_use_reduce_scatter(
             forward_batch
         )
-        hidden_states = self.mlp(hidden_states, forward_batch, use_reduce_scatter)

-        hidden_states, residual = self.layer_communicator.postprocess_layer(
-            hidden_states, residual, forward_batch
+        should_allreduce_fusion = (
+            self.layer_communicator.should_fuse_mlp_allreduce_with_next_layer(
+                forward_batch
+            )
         )
+        if isinstance(self.mlp, Qwen2MoeSparseMoeBlock):
+            hidden_states = self.mlp(hidden_states, forward_batch, use_reduce_scatter)
+        else:
+            hidden_states = self.mlp(
+                hidden_states, should_allreduce_fusion, use_reduce_scatter
+            )
+        if should_allreduce_fusion:
+            hidden_states._sglang_needs_allreduce_fusion = True
+        else:
+            hidden_states, residual = self.layer_communicator.postprocess_layer(
+                hidden_states, residual, forward_batch
+            )

         return hidden_states, residual

@@ -549,6 +564,8 @@ class Qwen3_5AttentionDecoderLayer(nn.Module):
             input_layernorm=self.input_layernorm,
             post_attention_layernorm=self.post_attention_layernorm,
             allow_reduce_scatter=True,
+            allow_allreduce_fusion=True,
+            is_last_layer=(layer_id == config.num_hidden_layers - 1),
         )

         self.alt_stream = alt_stream
@@ -633,11 +650,24 @@ class Qwen3_5AttentionDecoderLayer(nn.Module):
         use_reduce_scatter = self.layer_communicator.should_use_reduce_scatter(
             forward_batch
         )
-        hidden_states = self.mlp(hidden_states, forward_batch, use_reduce_scatter)

-        hidden_states, residual = self.layer_communicator.postprocess_layer(
-            hidden_states, residual, forward_batch
+        should_allreduce_fusion = (
+            self.layer_communicator.should_fuse_mlp_allreduce_with_next_layer(
+                forward_batch
+            )
         )
+        if isinstance(self.mlp, Qwen2MoeSparseMoeBlock):
+            hidden_states = self.mlp(hidden_states, forward_batch, use_reduce_scatter)
+        else:
+            hidden_states = self.mlp(
+                hidden_states, should_allreduce_fusion, use_reduce_scatter
+            )
+        if should_allreduce_fusion:
+            hidden_states._sglang_needs_allreduce_fusion = True
+        else:
+            hidden_states, residual = self.layer_communicator.postprocess_layer(
+                hidden_states, residual, forward_batch
+            )

         return hidden_states, residual

"""
    sections[i] = new_section
    break

if not found:
    print("ERROR: Could not find qwen3_5.py section in patch file", file=sys.stderr)
    sys.exit(1)

result = "".join(sections)
open(target, 'w').write(result)
print("Patch applied successfully.")
PYEOF
