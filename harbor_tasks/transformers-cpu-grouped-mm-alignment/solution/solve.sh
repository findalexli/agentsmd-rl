#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if already applied (the fix adds is_torch_less_or_equal import to moe.py)
if grep -q 'is_torch_less_or_equal' src/transformers/integrations/moe.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/docs/source/en/weightconverter.md b/docs/source/en/weightconverter.md
index eb9597732062..ae25d4691897 100644
--- a/docs/source/en/weightconverter.md
+++ b/docs/source/en/weightconverter.md
@@ -168,7 +168,6 @@ Operations are fully reversible. Saving reverses the conversions and returns the
 | [`MergeModulelist(dim)`] | [`SplitModulelist(dim)`] |
 | [`SplitModulelist(dim)`] | [`MergeModulelist(dim)`] |
 | [`Transpose(d0, d1)`] | [`Transpose(d1, d0)`] |
-| [`Force16BytesAlignment`] | [`Force16BytesAlignment`] (idempotent) |

 ### Chunk

@@ -248,10 +247,6 @@ WeightConverter(
 )
 ```

-### Force16BytesAlignment
-
-[`Force16BytesAlignment`] clones a tensor if it is not 16-byte aligned. This is required for `torch._grouped_mm` and TMA/SIMD operations. It is idempotent: applying it more than once has no additional effect.
-
 ## Operation chaining

 Operations can be chained to perform complex transformations. The operations execute in order, with each operation's output becoming the next operation's input.
diff --git a/src/transformers/conversion_mapping.py b/src/transformers/conversion_mapping.py
index ff1fd026dd6b..1e1d8fd98492 100755
--- a/src/transformers/conversion_mapping.py
+++ b/src/transformers/conversion_mapping.py
@@ -21,7 +21,6 @@
     Chunk,
     Concatenate,
     ErnieFuseAndSplitTextVisionExperts,
-    Force16BytesAlignment,
     MergeModulelist,
     Transpose,
     WeightConverter,
@@ -178,23 +177,6 @@ def _build_checkpoint_conversion_mapping():
             WeightRenaming("^norm.", "text_model.norm."),
             WeightRenaming("^layers.", "text_model.layers."),
         ],
-        "gpt_oss": [
-            # NOTE: These converters are only applied if the model is being loaded from pre-dequantized checkpoint.
-            # If you are dequantizing the model on the fly, these converters will be ignored because the tensors
-            # that match these patterns are only created after dequantization.
-            # That's not an issue for now since the dequantization converters already ensure 16 bytes alignment
-            # by enforcing contiguity.
-            WeightConverter(
-                source_patterns="mlp.experts.gate_up_proj$",
-                target_patterns="mlp.experts.gate_up_proj",
-                operations=[Force16BytesAlignment()],
-            ),
-            WeightConverter(
-                source_patterns="mlp.experts.down_proj$",
-                target_patterns="mlp.experts.down_proj",
-                operations=[Force16BytesAlignment()],
-            ),
-        ],
         "mixtral": [
             WeightRenaming(".block_sparse_moe.", ".mlp."),
             WeightConverter(
@@ -241,12 +223,12 @@ def _build_checkpoint_conversion_mapping():
             WeightConverter(
                 source_patterns="mlp.experts.gate_up_proj",
                 target_patterns="mlp.experts.gate_up_proj",
-                operations=[Transpose(1, 2, check_dims=True), Force16BytesAlignment()],
+                operations=[Transpose(1, 2, check_dims=True)],
             ),
             WeightConverter(
                 source_patterns="mlp.experts.down_proj",
                 target_patterns="mlp.experts.down_proj",
-                operations=[Transpose(1, 2, check_dims=True), Force16BytesAlignment()],
+                operations=[Transpose(1, 2, check_dims=True)],
             ),
         ],
         "phimoe": [
@@ -458,12 +440,12 @@ def _build_checkpoint_conversion_mapping():
                 "mlp.experts.*.up_proj.weight",
             ],
             target_patterns="mlp.experts.gate_up_proj",
-            operations=[MergeModulelist(dim=0), Concatenate(dim=1), Force16BytesAlignment()],
+            operations=[MergeModulelist(dim=0), Concatenate(dim=1)],
         ),
         WeightConverter(
             source_patterns="mlp.experts.*.down_proj.weight",
             target_patterns="mlp.experts.down_proj",
-            operations=[MergeModulelist(dim=0), Force16BytesAlignment()],
+            operations=[MergeModulelist(dim=0)],
         ),
     ]
     mapping["minimax_m2"] = mapping["mixtral"].copy()
@@ -480,12 +462,12 @@ def _build_checkpoint_conversion_mapping():
                 "mlp.experts.*.up_proj.weight",
             ],
             target_patterns="mlp.experts.gate_up_proj",
-            operations=[MergeModulelist(dim=0), Concatenate(dim=1), Force16BytesAlignment()],
+            operations=[MergeModulelist(dim=0), Concatenate(dim=1)],
         ),
         WeightConverter(
             source_patterns="mlp.experts.*.down_proj.weight",
             target_patterns="mlp.experts.down_proj",
-            operations=[MergeModulelist(dim=0), Force16BytesAlignment()],
+            operations=[MergeModulelist(dim=0)],
         ),
     ]

@@ -563,13 +545,6 @@ def get_model_conversion_mapping(

     # Add the ones from the quantizer as well if provided
     if hf_quantizer is not None:
-        # NOTE: Since get_weight_conversions() only serve to dequantize, we would normally want to apply them first.
-        # However, for now it's not possible to cascade converters (i.e., applying model-specific conversions on top
-        # of tensors created by the dequantization conversions)
-        # This means that if a model has model-specific conversions and is being dequantized, the model-specific conversion
-        # that relies on tensors created by dequantization conversions will not be applied.
-        # GptOss example: with Mxfp4Config(dequantize=True), Force16BytesAlignment converters are ignored because the tensors
-        # "mlp.experts.gate_up_proj$" and "mlp.experts.down_proj$" are only created after dequantization conversions are applied.
         weight_conversions.extend(hf_quantizer.get_weight_conversions())

     return weight_conversions
diff --git a/src/transformers/core_model_loading.py b/src/transformers/core_model_loading.py
index f6690ff4c790..9bcd625d2840 100644
--- a/src/transformers/core_model_loading.py
+++ b/src/transformers/core_model_loading.py
@@ -452,42 +452,6 @@ def reverse_op(self) -> ConversionOps:
         return ErnieFuseAndSplitTextVisionExperts(stack_dim=self.stack_dim, concat_dim=self.concat_dim)


-class Force16BytesAlignment(ConversionOps):
-    """
-    Ensures that the given tensor is 16-bytes aligned in memory and clones it if not.
-    This guarantees 16-bytes alignment for kernels / implementations that use TMA or SIMD instructions like torch.nn.functional.grouped_mm.
-    """
-
-    @torch.no_grad()
-    def convert(
-        self, input_dict: dict[str, torch.Tensor], source_patterns: list[str], target_patterns: list[str], **kwargs
-    ) -> dict[str, torch.Tensor]:
-        target_pattern = self.get_target_pattern(input_dict, source_patterns, target_patterns)
-        tensors = next(iter(input_dict.values()))
-        tensor = tensors[0] if isinstance(tensors, list) else tensors
-        tensor = tensor.clone() if tensor.data_ptr() % 16 != 0 else tensor
-        return {target_pattern: tensor}
-
-    def get_target_pattern(
-        self, input_dict: dict[str, torch.Tensor], source_patterns: list[str], target_patterns: list[str]
-    ) -> str:
-        if len(input_dict) != 1:
-            raise ValueError("Undefined Operation encountered!")
-        # Here it's the first operation of a chain, so return the source
-        if len(target_patterns) > 1:
-            if len(source_patterns) == 1:
-                return source_patterns[0]
-            else:
-                raise ValueError("Undefined Operation encountered!")
-        # Here it's the only operation, or the last operation in a chain, so we return the target
-        else:
-            return target_patterns[0]
-
-    @property
-    def reverse_op(self) -> ConversionOps:
-        return Force16BytesAlignment()
-
-
 def process_target_pattern(pattern: str) -> tuple[str, str | None]:
     """
     Process a target pattern for reverse mapping (when targets become sources).
diff --git a/src/transformers/integrations/moe.py b/src/transformers/integrations/moe.py
index 8c383eb73f21..1ad461ccb96e 100644
--- a/src/transformers/integrations/moe.py
+++ b/src/transformers/integrations/moe.py
@@ -17,7 +17,7 @@

 from ..utils import logging
 from ..utils.generic import GeneralInterface
-from ..utils.import_utils import is_torch_available, is_torchdynamo_compiling
+from ..utils.import_utils import is_torch_available, is_torch_less_or_equal, is_torchdynamo_compiling


 if is_torch_available():
@@ -261,8 +261,18 @@ def _can_use_grouped_mm(input: torch.Tensor, weight: torch.Tensor, offs: torch.T
     Returns:
         `bool`: True if grouped_mm can be used, False otherwise.
     """
-    if is_torchdynamo_compiling() and weight.dtype != torch.bfloat16:
-        # torch.grouped_mm is not supported in torch.compile with dtypes other than bfloat16
+    if (is_torchdynamo_compiling() and weight.dtype != torch.bfloat16) or (
+        weight.device.type == "cpu"
+        # accept_dev=True is necessary for "+cpu"/"+xpu" etc.
+        and is_torch_less_or_equal("2.10.0", accept_dev=True)
+        and (weight.data_ptr() % 16 != 0 or input.data_ptr() % 16 != 0)
+    ):
+        # Under the following conditions we cannot use torch.grouped_mm and have to fall back:
+        # 1. torch.grouped_mm is not supported in torch.compile / inductor with dtypes other than bf16
+        # 2. Before PyTorch 2.11, torch.grouped_mm on CPU required 16 bytes alignment which is not
+        #    guaranteed for tensors loaded using memmap (e.g. using safetensors lazy tensor loading)
+        #    and not really necessary because the cpu path uses a fallback for-loop implementation.
+        #    issue: https://github.com/pytorch/pytorch/issues/172440
         return False

     return hasattr(torch.nn.functional, "grouped_mm") or hasattr(torch, "_grouped_mm")
diff --git a/tests/vlm_tester.py b/tests/vlm_tester.py
index 5d3b2d05d94b..c40b42785836 100644
--- a/tests/vlm_tester.py
+++ b/tests/vlm_tester.py
@@ -84,7 +84,7 @@ def __init__(self, parent, **kwargs):
         kwargs.setdefault("num_hidden_layers", 2)
         kwargs.setdefault("num_attention_heads", 2)
         kwargs.setdefault("num_key_value_heads", 2)
-        kwargs.setdefault("intermediate_size", 37)
+        kwargs.setdefault("intermediate_size", 32)  # Keep this divisible by 8 for fp16/bf16/fp32 16-bytes alignment
         kwargs.setdefault("hidden_act", "gelu")
         kwargs.setdefault("hidden_dropout_prob", 0.1)
         kwargs.setdefault("attention_probs_dropout_prob", 0.1)

PATCH

echo "Patch applied successfully."
