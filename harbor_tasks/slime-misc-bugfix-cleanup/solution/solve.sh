#!/usr/bin/env bash
set -euo pipefail
cd /workspace/slime

# Idempotent: skip if already applied
grep -q 'from_hf_pretrained(load_path' slime/backends/megatron_utils/checkpoint.py && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/slime/backends/megatron_utils/checkpoint.py b/slime/backends/megatron_utils/checkpoint.py
index 8c7cd5317..5fc789615 100644
--- a/slime/backends/megatron_utils/checkpoint.py
+++ b/slime/backends/megatron_utils/checkpoint.py
@@ -135,7 +135,7 @@ def _load_checkpoint_hf(ddp_model, optimizer, args, load_path: str):
     logger.info(f"Load checkpoint from HuggingFace model into Megatron (path={load_path})")

     with megatron_bridge_utils.patch_megatron_model(ddp_model):
-        bridge = AutoBridge.from_hf_pretrained(args.hf_checkpoint, trust_remote_code=True)
+        bridge = AutoBridge.from_hf_pretrained(load_path, trust_remote_code=True)
         bridge.load_hf_weights(ddp_model)

     # Copied from Megatron-core :: load_checkpoint (with simplifications)
diff --git a/slime/backends/megatron_utils/data.py b/slime/backends/megatron_utils/data.py
index 19be99f3c..8a7f768b3 100644
--- a/slime/backends/megatron_utils/data.py
+++ b/slime/backends/megatron_utils/data.py
@@ -164,18 +164,14 @@ def get_batch(
     multimodal_train_inputs = batch.get("multimodal_train_inputs", None)
     if multimodal_train_inputs is not None:
         multimodal_data = {}  # key -> concatenated tensor
-        multimodal_num_items = {}  # key -> list of item counts per sequence
         for mm_input_dict in multimodal_train_inputs:
             if mm_input_dict is not None:
                 for key, mm_tensor in mm_input_dict.items():
                     if key not in multimodal_data:
                         multimodal_data[key] = mm_tensor
-                        multimodal_num_items[key] = [mm_tensor.size(0)]
                     else:
                         multimodal_data[key] = torch.cat([multimodal_data[key], mm_tensor], dim=0)
-                        multimodal_num_items[key].append(mm_tensor.size(0))
         batch["multimodal_train_inputs"] = multimodal_data
-        batch["multimodal_num_items"] = multimodal_num_items

     return batch

diff --git a/slime/utils/processing_utils.py b/slime/utils/processing_utils.py
index 56a002a74..fb652e73d 100644
--- a/slime/utils/processing_utils.py
+++ b/slime/utils/processing_utils.py
@@ -26,7 +26,11 @@ def build_processor_kwargs(multimodal_inputs: dict | None = None) -> dict:
     result = dict(multimodal_inputs) if multimodal_inputs else {}

     # return_tensors=None for text (input_ids as lists), "pt" for modality-specific outputs
-    result["text_kwargs"] = {**result.get("text_kwargs", {}), "return_tensors": None}
+    result["text_kwargs"] = {
+        **result.get("text_kwargs", {}),
+        "return_tensors": None,
+        "return_mm_token_type_ids": False,
+    }
     for key in ("audio_kwargs", "images_kwargs", "videos_kwargs"):
         if key in result:
             result[key] = {**result[key], **modality_forced}
PATCH
