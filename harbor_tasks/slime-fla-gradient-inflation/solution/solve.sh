#!/usr/bin/env bash
set -euo pipefail
cd /workspace/slime

# Idempotent: skip if already applied
if grep -q 'tensor_parallel_output_grad=False' slime_plugins/models/hf_attention.py; then
    echo "Patch already applied"
else
    git apply --whitespace=nowarn - <<'PATCH'
diff --git a/slime/utils/reloadable_process_group.py b/slime/utils/reloadable_process_group.py
index a8ea33a909..66055a352f 100644
--- a/slime/utils/reloadable_process_group.py
+++ b/slime/utils/reloadable_process_group.py
@@ -296,7 +296,7 @@ def reload_process_groups():
 def _wrap_low_level_call():
     try:
         mem_info = available_memory()
-        if mem_info["free_GB"] < 5:
+        if mem_info["free_GB"] < 3:
             clear_memory()
         yield
     except Exception as e:
diff --git a/slime_plugins/models/hf_attention.py b/slime_plugins/models/hf_attention.py
index c353ae7b29..26b04d6d3b 100644
--- a/slime_plugins/models/hf_attention.py
+++ b/slime_plugins/models/hf_attention.py
@@ -1,4 +1,6 @@
 from abc import ABC, abstractmethod
+import json
+import os

 import torch
 import torch.distributed as dist
@@ -6,7 +8,56 @@
 from megatron.core.inference.contexts import BaseInferenceContext
 from megatron.core.packed_seq_params import PackedSeqParams
 from megatron.core.transformer.module import MegatronModule
-from transformers import AutoConfig
+
+
+def _load_hf_config(checkpoint_path):
+    """Load HF config with fallback for unsupported model types."""
+    try:
+        from transformers import AutoConfig
+
+        return AutoConfig.from_pretrained(checkpoint_path, trust_remote_code=True)
+    except (ValueError, KeyError):
+        config_path = os.path.join(checkpoint_path, "config.json")
+        with open(config_path) as f:
+            config_dict = json.load(f)
+
+        _DTYPE_MAP = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}
+
+        def _fix_dtype(d):
+            if "torch_dtype" in d:
+                d["torch_dtype"] = _DTYPE_MAP.get(d["torch_dtype"], d["torch_dtype"])
+            if "dtype" in d:
+                d["dtype"] = _DTYPE_MAP.get(d["dtype"], d["dtype"])
+
+        _fix_dtype(config_dict)
+        ns = type("HFConfig", (), config_dict)()
+        if "text_config" in config_dict:
+            _fix_dtype(config_dict["text_config"])
+            ns.text_config = type("TextConfig", (), config_dict["text_config"])()
+        return ns
+
+
+class _AllGatherForDuplicatedComputation(torch.autograd.Function):
+    """All-gather whose backward just returns the local gradient slice (no reduce).
+
+    Use this instead of ``dist.nn.all_gather`` when the computation after the
+    gather is *duplicated* across ranks (same weights, same full input ->
+    identical gradients).  The default ``all_gather`` backward performs a
+    reduce-scatter, which incorrectly sums ``world_size`` identical copies of
+    the gradient.
+    """
+
+    @staticmethod
+    def forward(ctx, x, group):
+        ctx.group = group
+        ctx.rank = dist.get_rank(group=group)
+        out = [torch.empty_like(x) for _ in range(dist.get_world_size(group=group))]
+        dist.all_gather(out, x.contiguous(), group=group)
+        return tuple(out)
+
+    @staticmethod
+    def backward(ctx, *grads):
+        return grads[ctx.rank], None


 class HuggingfaceAttention(MegatronModule, ABC):
@@ -30,7 +81,7 @@ def __init__(
         # Note that megatron layer_number starts at 1
         self.layer_number = layer_number
         self.hf_layer_idx = layer_number - 1
-        self.hf_config = AutoConfig.from_pretrained(args.hf_checkpoint, trust_remote_code=True)
+        self.hf_config = _load_hf_config(args.hf_checkpoint)
         # hardcode to fa2 at the moment.
         self.hf_config._attn_implementation = "flash_attention_2"

@@ -54,15 +105,22 @@ def forward(
         cu_seqlens = packed_seq_params.cu_seqlens_q

         if self.args.sequence_parallel:
+            # tensor_parallel_output_grad=False: the linear attention after this
+            # gather is NOT TP-sharded (duplicated on all ranks), so the backward
+            # should split (not reduce-scatter) to avoid inflating gradients by TP.
             hidden_states = tensor_parallel.gather_from_sequence_parallel_region(
-                hidden_states, group=mpu.get_tensor_model_parallel_group()
+                hidden_states,
+                tensor_parallel_output_grad=False,
+                group=mpu.get_tensor_model_parallel_group(),
             )

         if mpu.get_context_parallel_world_size() > 1:
             cp_size = mpu.get_context_parallel_world_size()
-            hidden_states_list = dist.nn.all_gather(
+            # Use custom all-gather whose backward returns local gradient
+            # instead of reduce-scatter, since the computation is duplicated.
+            hidden_states_list = _AllGatherForDuplicatedComputation.apply(
                 hidden_states,
-                group=mpu.get_context_parallel_group(),
+                mpu.get_context_parallel_group(),
             )

             # TODO: preprocess this for each batch to prevent tolist in the training step
diff --git a/slime_plugins/models/qwen3_5.py b/slime_plugins/models/qwen3_5.py
index 11ccb2d1ad..a796c8c49c 100644
--- a/slime_plugins/models/qwen3_5.py
+++ b/slime_plugins/models/qwen3_5.py
@@ -1,6 +1,4 @@
 import copy
-import json
-import os

 import torch
 import torch.nn as nn
@@ -11,32 +9,13 @@
 from megatron.core.transformer.transformer_layer import get_transformer_layer_offset
 from transformers.activations import ACT2FN

-
-def _load_hf_config(checkpoint_path):
-    """Load HF config, handling cases where transformers doesn't know the model type."""
-    try:
-        from transformers import AutoConfig
-
-        return AutoConfig.from_pretrained(checkpoint_path, trust_remote_code=True)
-    except (ValueError, KeyError):
-        # Fallback: load config.json directly as a SimpleNamespace
-        config_path = os.path.join(checkpoint_path, "config.json")
-        with open(config_path) as f:
-            config_dict = json.load(f)
-        # If there's a text_config, also make it a namespace
-        ns = type("HFConfig", (), config_dict)()
-        if "text_config" in config_dict:
-            ns.text_config = type("TextConfig", (), config_dict["text_config"])()
-        return ns
-
-
 try:
     from fla.modules import FusedRMSNormGated, ShortConvolution
     from fla.ops.gated_delta_rule import chunk_gated_delta_rule
 except ImportError:
     pass

-from .hf_attention import HuggingfaceAttention
+from .hf_attention import HuggingfaceAttention, _load_hf_config


 def _get_text_config(hf_config):
@@ -226,6 +205,14 @@ def get_qwen3_5_spec(args, config, vp_stage):
     hf_config = _load_hf_config(args.hf_checkpoint)
     text_config = _get_text_config(hf_config)

+    # Compute layer_types if the config class doesn't expose it
+    if not hasattr(text_config, "layer_types"):
+        interval = getattr(text_config, "full_attention_interval", 4)
+        n = text_config.num_hidden_layers
+        text_config.layer_types = [
+            "full_attention" if (i + 1) % interval == 0 else "linear_attention" for i in range(n)
+        ]
+
     for layer_id in range(num_layers_to_build):
         if text_config.layer_types[layer_id + offset] == "linear_attention":
             layer_specs = copy.deepcopy(transformer_layer_spec.layer_specs[layer_id])
diff --git a/slime_plugins/models/qwen3_next.py b/slime_plugins/models/qwen3_next.py
index 482dcfe92f..c6026af869 100644
--- a/slime_plugins/models/qwen3_next.py
+++ b/slime_plugins/models/qwen3_next.py
@@ -7,7 +7,7 @@
 from megatron.core.transformer.spec_utils import ModuleSpec
 from megatron.core.transformer.transformer_block import get_num_layers_to_build
 from megatron.core.transformer.transformer_layer import get_transformer_layer_offset
-from transformers import AutoConfig
+from .hf_attention import _load_hf_config
 from transformers.activations import ACT2FN

 try:
@@ -214,7 +214,15 @@ def get_qwen3_next_spec(args, config, vp_stage):
     num_layers_to_build = get_num_layers_to_build(config, vp_stage=vp_stage)
     offset = get_transformer_layer_offset(config, vp_stage=vp_stage)

-    hf_config = AutoConfig.from_pretrained(args.hf_checkpoint, trust_remote_code=True)
+    hf_config = _load_hf_config(args.hf_checkpoint)
+
+    # Compute layer_types if the config class doesn't expose it
+    if not hasattr(hf_config, "layer_types"):
+        interval = getattr(hf_config, "full_attention_interval", 4)
+        n = hf_config.num_hidden_layers
+        hf_config.layer_types = [
+            "full_attention" if (i + 1) % interval == 0 else "linear_attention" for i in range(n)
+        ]

     for layer_id in range(num_layers_to_build):
         if hf_config.layer_types[layer_id + offset] == "linear_attention":

PATCH
fi

# Format the modified files to satisfy isort and black checks
pip install -q isort black
isort --profile=black slime_plugins/models/hf_attention.py slime_plugins/models/qwen3_5.py slime_plugins/models/qwen3_next.py slime/utils/reloadable_process_group.py
black slime_plugins/models/hf_attention.py slime_plugins/models/qwen3_5.py slime_plugins/models/qwen3_next.py slime/utils/reloadable_process_group.py
