#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotency check: if _format_dtype_mismatch_summary already exists, patch is applied
if grep -q '_format_dtype_mismatch_summary' python/sglang/multimodal_gen/runtime/loader/fsdp_load.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/multimodal_gen/runtime/loader/fsdp_load.py b/python/sglang/multimodal_gen/runtime/loader/fsdp_load.py
index f2f7c7709783..385931b19e02 100644
--- a/python/sglang/multimodal_gen/runtime/loader/fsdp_load.py
+++ b/python/sglang/multimodal_gen/runtime/loader/fsdp_load.py
@@ -6,6 +6,7 @@
 # Copyright 2024 The TorchTune Authors.
 # Copyright 2025 The sglang-diffusion Authors.

+from collections import Counter, defaultdict
 from collections.abc import Callable, Generator
 from itertools import chain
 from typing import Any
@@ -40,6 +41,28 @@

 logger = init_logger(__name__)

+_QUANTIZED_DTYPES = (
+    torch.uint8,
+    torch.float8_e4m3fn,
+    torch.float8_e5m2,
+    torch.int8,
+)
+_DTYPE_MISMATCH_EXAMPLE_LIMIT = 3
+
+
+def _format_dtype_mismatch_summary(
+    mismatch_counts: Counter[tuple[torch.dtype, torch.dtype]],
+    mismatch_examples: dict[tuple[torch.dtype, torch.dtype], list[str]],
+) -> str:
+    parts: list[str] = []
+    for (checkpoint_dtype, target_dtype), count in mismatch_counts.items():
+        examples = mismatch_examples[(checkpoint_dtype, target_dtype)]
+        part = f"{checkpoint_dtype}->{target_dtype} x{count}"
+        if examples:
+            part += f" (e.g. {', '.join(examples)})"
+        parts.append(part)
+    return "; ".join(parts)
+

 def _make_param_like(
     actual_param: torch.nn.Parameter, tensor: torch.Tensor
@@ -272,6 +295,18 @@ def load_model_from_full_model_state_dict(

     sharded_sd = {}
     skipped_checkpoint_keys: list[str] = []
+    non_quantized_dtype_mismatch_counts: Counter[tuple[torch.dtype, torch.dtype]] = (
+        Counter()
+    )
+    non_quantized_dtype_mismatch_examples: dict[
+        tuple[torch.dtype, torch.dtype], list[str]
+    ] = defaultdict(list)
+    quantized_dtype_mismatch_counts: Counter[tuple[torch.dtype, torch.dtype]] = (
+        Counter()
+    )
+    quantized_dtype_mismatch_examples: dict[
+        tuple[torch.dtype, torch.dtype], list[str]
+    ] = defaultdict(list)

     # shard from loaded state_dict, custom_param_sd -> sharded_sd
     for target_param_name in sorted_param_names:
@@ -296,32 +331,29 @@ def load_model_from_full_model_state_dict(
         else:
             target_dtype = meta_sharded_param.dtype

-        _QUANTIZED_DTYPES = (
-            torch.uint8,
-            torch.float8_e4m3fn,
-            torch.float8_e5m2,
-            torch.int8,
-        )
         if full_tensor.dtype != target_dtype:
+            mismatch_key = (full_tensor.dtype, target_dtype)
             if (
                 full_tensor.dtype in _QUANTIZED_DTYPES
                 or target_dtype in _QUANTIZED_DTYPES
             ):
-                logger.warning(
-                    "Dtype mismatch for quantized parameter %s: "
-                    "checkpoint has %s, model expects %s",
-                    target_param_name,
-                    full_tensor.dtype,
-                    target_dtype,
-                )
+                quantized_dtype_mismatch_counts[mismatch_key] += 1
+                if (
+                    len(quantized_dtype_mismatch_examples[mismatch_key])
+                    < _DTYPE_MISMATCH_EXAMPLE_LIMIT
+                ):
+                    quantized_dtype_mismatch_examples[mismatch_key].append(
+                        target_param_name
+                    )
             else:
-                logger.warning(
-                    "Dtype mismatch for %s: checkpoint has %s, model expects %s. "
-                    "Casting checkpoint tensor to the target dtype during load.",
-                    target_param_name,
-                    full_tensor.dtype,
-                    target_dtype,
-                )
+                non_quantized_dtype_mismatch_counts[mismatch_key] += 1
+                if (
+                    len(non_quantized_dtype_mismatch_examples[mismatch_key])
+                    < _DTYPE_MISMATCH_EXAMPLE_LIMIT
+                ):
+                    non_quantized_dtype_mismatch_examples[mismatch_key].append(
+                        target_param_name
+                    )

         if not hasattr(meta_sharded_param, "device_mesh"):
             full_tensor = full_tensor.to(device=device, dtype=target_dtype)
@@ -378,6 +410,28 @@ def load_model_from_full_model_state_dict(

     model.reverse_param_names_mapping = reverse_param_names_mapping

+    if non_quantized_dtype_mismatch_counts:
+        logger.debug(
+            "Casting checkpoint tensors to target dtype during load: %s",
+            _format_dtype_mismatch_summary(
+                non_quantized_dtype_mismatch_counts,
+                non_quantized_dtype_mismatch_examples,
+            ),
+            main_process_only=True,
+            local_main_process_only=True,
+        )
+
+    if quantized_dtype_mismatch_counts:
+        logger.warning(
+            "Dtype mismatches detected for quantized parameters during load: %s",
+            _format_dtype_mismatch_summary(
+                quantized_dtype_mismatch_counts,
+                quantized_dtype_mismatch_examples,
+            ),
+            main_process_only=True,
+            local_main_process_only=True,
+        )
+
     if skipped_checkpoint_keys:
         logger.warning(
             "Checkpoint keys not loaded (no matching model parameter) %s",

PATCH

echo "Patch applied successfully."
