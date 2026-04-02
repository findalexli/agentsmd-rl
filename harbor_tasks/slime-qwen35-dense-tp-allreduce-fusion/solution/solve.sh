#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

TARGET="docker/patch/latest/sglang.patch"

# Idempotency check: if fix is already applied, exit
if grep -q 'should_fuse_mlp_allreduce_with_next_layer' "$TARGET" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/docker/patch/latest/sglang.patch b/docker/patch/latest/sglang.patch
index 57d7f09ac0..0cf9731bb0 100644
--- a/docker/patch/latest/sglang.patch
+++ b/docker/patch/latest/sglang.patch
@@ -2517,7 +2517,7 @@ index 2cf813bce..1250c49e4 100644
      weights_out_dict = dict(weights_in)

 diff --git a/python/sglang/srt/models/qwen3_5.py b/python/sglang/srt/models/qwen3_5.py
-index f01225487..145ee410c 100644
+index f012254..1dad8bb 100644
 --- a/python/sglang/srt/models/qwen3_5.py
 +++ b/python/sglang/srt/models/qwen3_5.py
 @@ -372,6 +372,7 @@ class Qwen3_5LinearDecoderLayer(nn.Module):
@@ -2528,7 +2528,35 @@ index f01225487..145ee410c 100644
          )

      def forward(
-@@ -549,6 +550,7 @@ class Qwen3_5AttentionDecoderLayer(nn.Module):
+@@ -400,11 +401,24 @@ class Qwen3_5LinearDecoderLayer(nn.Module):
+         use_reduce_scatter = self.layer_communicator.should_use_reduce_scatter(
+             forward_batch
+         )
+-        hidden_states = self.mlp(hidden_states, forward_batch, use_reduce_scatter)
+
+-        hidden_states, residual = self.layer_communicator.postprocess_layer(
+-            hidden_states, residual, forward_batch
++        should_allreduce_fusion = (
++            self.layer_communicator.should_fuse_mlp_allreduce_with_next_layer(
++                forward_batch
++            )
+         )
++        if isinstance(self.mlp, Qwen2MoeSparseMoeBlock):
++            hidden_states = self.mlp(hidden_states, forward_batch, use_reduce_scatter)
++        else:
++            hidden_states = self.mlp(
++                hidden_states, should_allreduce_fusion, use_reduce_scatter
++            )
++        if should_allreduce_fusion:
++            hidden_states._sglang_needs_allreduce_fusion = True
++        else:
++            hidden_states, residual = self.layer_communicator.postprocess_layer(
++                hidden_states, residual, forward_batch
++            )
+
+         return hidden_states, residual
+
+@@ -549,6 +563,7 @@ class Qwen3_5AttentionDecoderLayer(nn.Module):
              input_layernorm=self.input_layernorm,
              post_attention_layernorm=self.post_attention_layernorm,
              allow_reduce_scatter=True,
@@ -2536,6 +2564,34 @@ index f01225487..145ee410c 100644
          )

          self.alt_stream = alt_stream
+@@ -633,11 +648,24 @@ class Qwen3_5AttentionDecoderLayer(nn.Module):
+         use_reduce_scatter = self.layer_communicator.should_use_reduce_scatter(
+             forward_batch
+         )
+-        hidden_states = self.mlp(hidden_states, forward_batch, use_reduce_scatter)
+
+-        hidden_states, residual = self.layer_communicator.postprocess_layer(
+-            hidden_states, residual, forward_batch
++        should_allreduce_fusion = (
++            self.layer_communicator.should_fuse_mlp_allreduce_with_next_layer(
++                forward_batch
++            )
+         )
++        if isinstance(self.mlp, Qwen2MoeSparseMoeBlock):
++            hidden_states = self.mlp(hidden_states, forward_batch, use_reduce_scatter)
++        else:
++            hidden_states = self.mlp(
++                hidden_states, should_allreduce_fusion, use_reduce_scatter
++            )
++        if should_allreduce_fusion:
++            hidden_states._sglang_needs_allreduce_fusion = True
++        else:
++            hidden_states, residual = self.layer_communicator.postprocess_layer(
++                hidden_states, residual, forward_batch
++            )
+
+         return hidden_states, residual
+
 diff --git a/python/sglang/srt/models/qwen3_vl.py b/python/sglang/srt/models/qwen3_vl.py
 index d641826e3..3abc39ef3 100644
 --- a/python/sglang/srt/models/qwen3_vl.py

PATCH

echo "Patch applied successfully."
