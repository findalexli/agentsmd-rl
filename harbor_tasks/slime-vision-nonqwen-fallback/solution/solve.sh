#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotency check: skip if already applied
if grep -q '_extract_images_from_messages' slime/utils/processing_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/backends/megatron_utils/actor.py b/slime/backends/megatron_utils/actor.py
index af4880cf4..029cefd48 100644
--- a/slime/backends/megatron_utils/actor.py
+++ b/slime/backends/megatron_utils/actor.py
@@ -5,6 +5,7 @@
 from argparse import Namespace
 from contextlib import nullcontext

+import numpy as np
 import ray
 import torch
 import torch.distributed as dist
@@ -204,7 +205,14 @@ def _get_rollout_data(self, rollout_data_ref: Box) -> RolloutBatch:
             # Move multimodal training tensors to GPU in advance
             rollout_data["multimodal_train_inputs"] = [
                 (
-                    {key: tensor.to(device=torch.cuda.current_device()) for key, tensor in mm_dict.items()}
+                    {
+                        key: (
+                            torch.from_numpy(v.copy()).to(device=torch.cuda.current_device())
+                            if isinstance(v, np.ndarray)
+                            else v.to(device=torch.cuda.current_device())
+                        )
+                        for key, v in mm_dict.items()
+                    }
                     if mm_dict is not None
                     else None
                 )
diff --git a/slime/rollout/sglang_rollout.py b/slime/rollout/sglang_rollout.py
index 89d9bcff1..7471e2580 100644
--- a/slime/rollout/sglang_rollout.py
+++ b/slime/rollout/sglang_rollout.py
@@ -165,13 +165,21 @@ async def generate(args: Namespace, sample: Sample, sampling_params: dict[str, A
     if args.use_rollout_routing_replay:
         payload["return_routed_experts"] = True

-    if sample.multimodal_inputs and sample.multimodal_inputs["images"]:
+    has_multimodal = sample.multimodal_inputs and sample.multimodal_inputs.get("images")
+    if has_multimodal:
         image_data = sample.multimodal_inputs["images"]
         payload["image_data"] = [encode_image_for_rollout_engine(image) for image in image_data]

     # Use existing tokens for multi-turn or tokenize the new prompt
     if len(sample.response) > 0:
         payload["input_ids"] = sample.tokens
+    elif has_multimodal:
+        # For multimodal first-turn: send text so SGLang handles image token
+        # expansion internally (the processor-expanded input_ids have N patch
+        # tokens per image which would mismatch the image_data count).
+        payload["text"] = sample.prompt
+        if not sample.tokens:
+            sample.tokens = prompt_ids
     else:
         payload["input_ids"] = prompt_ids
         if not sample.tokens:  # Initialize sample.tokens for the first turn
diff --git a/slime/utils/processing_utils.py b/slime/utils/processing_utils.py
index 879346627..56a002a74 100644
--- a/slime/utils/processing_utils.py
+++ b/slime/utils/processing_utils.py
@@ -1,7 +1,10 @@
 import base64
 import io
+import json
 import logging
+from pathlib import Path

+from PIL import Image
 from transformers import AutoProcessor, AutoTokenizer, PreTrainedTokenizerBase, ProcessorMixin

 logger = logging.getLogger(__name__)
@@ -33,6 +36,48 @@ def build_processor_kwargs(multimodal_inputs: dict | None = None) -> dict:
     return result


+def _try_load_glm4v_processor(name_or_path: str, **kwargs):
+    """Fallback: manually construct a Glm4vProcessor for GLM-4.6V / GLM-4.5V models.
+
+    AutoProcessor fails for these models on transformers < 5.0 because
+    the Glm46VProcessor / Glm4vMoeProcessor classes are not registered.
+    The underlying Glm4vProcessor (non-MoE) works for both variants since
+    they share the same vision architecture.
+    """
+    try:
+        from transformers.models.glm4v.image_processing_glm4v import Glm4vImageProcessor
+        from transformers.models.glm4v.processing_glm4v import Glm4vProcessor
+        from transformers.models.glm4v.video_processing_glm4v import Glm4vVideoProcessor
+    except ImportError:
+        return None
+
+    pp_path = Path(name_or_path) / "preprocessor_config.json"
+    vp_path = Path(name_or_path) / "video_preprocessor_config.json"
+    if not pp_path.exists():
+        return None
+
+    skip_keys = {"image_processor_type", "processor_class", "video_processor_type"}
+    with open(pp_path) as f:
+        pp_cfg = {k: v for k, v in json.load(f).items() if k not in skip_keys}
+    image_processor = Glm4vImageProcessor(**pp_cfg)
+
+    video_processor = None
+    if vp_path.exists():
+        with open(vp_path) as f:
+            vp_cfg = {k: v for k, v in json.load(f).items() if k not in skip_keys}
+        video_processor = Glm4vVideoProcessor(**vp_cfg)
+
+    tokenizer = AutoTokenizer.from_pretrained(name_or_path, **kwargs)
+    proc = Glm4vProcessor(
+        image_processor=image_processor,
+        tokenizer=tokenizer,
+        video_processor=video_processor,
+        chat_template=tokenizer.chat_template,
+    )
+    logger.info(f"Loaded Glm4vProcessor manually for {name_or_path}")
+    return proc
+
+
 def load_processor(name_or_path: str, **kwargs):
     try:
         proc = AutoProcessor.from_pretrained(name_or_path, **kwargs)
@@ -40,25 +85,67 @@ def load_processor(name_or_path: str, **kwargs):
         logger.warning(f"Failed to load processor from {name_or_path}: {e}")
         proc = None

-    # If HF returned a tokenizer, discard it.
+    # If HF returned a tokenizer instead of a proper processor, discard it.
     if isinstance(proc, PreTrainedTokenizerBase) or not isinstance(proc, ProcessorMixin):
-        proc = None
+        # Fallback: try to construct a GLM-4.6V / GLM-4.5V processor manually.
+        proc = _try_load_glm4v_processor(name_or_path, **kwargs)

     return proc


+def _extract_images_from_messages(messages):
+    """Extract PIL images from chat messages containing multimodal content.
+
+    Handles base64 strings (with or without data: URI prefix), file paths,
+    and PIL Image objects embedded in message content dicts.
+    """
+    images = []
+    for msg in messages:
+        content = msg.get("content", [])
+        if not isinstance(content, list):
+            continue
+        for item in content:
+            if not isinstance(item, dict) or item.get("type") != "image":
+                continue
+            image_data = item.get("image")
+            if image_data is None:
+                continue
+            if isinstance(image_data, Image.Image):
+                images.append(image_data)
+            elif isinstance(image_data, str):
+                if image_data.startswith("data:"):
+                    _, encoded = image_data.split(",", 1)
+                    images.append(Image.open(io.BytesIO(base64.b64decode(encoded))))
+                else:
+                    try:
+                        raw = base64.b64decode(image_data)
+                        images.append(Image.open(io.BytesIO(raw)))
+                    except Exception:
+                        # Not base64 — try as file path
+                        images.append(Image.open(image_data))
+    return images
+
+
 def process_vision_info(prompt, processor):
-    # TODO: temporary solution, will write image utils for slime later
-    from qwen_vl_utils import process_vision_info as qwen_process_vision_info
-
-    if hasattr(processor.image_processor, "patch_size"):
-        image_patch_size = processor.image_processor.patch_size
-    else:
-        logger.info(f"Using default patch size: {DEFAULT_PATCH_SIZE}")
-        image_patch_size = DEFAULT_PATCH_SIZE
-    images, videos = qwen_process_vision_info(prompt, image_patch_size=image_patch_size)
-    multimodal_inputs = {"images": images, "videos": videos}
-    return multimodal_inputs
+    """Extract PIL images (and videos) from the message list for training.
+
+    Tries qwen_vl_utils first (Qwen VL family), falls back to generic
+    extraction for other models (e.g. GLM-4.6V).
+    """
+    try:
+        from qwen_vl_utils import process_vision_info as qwen_process_vision_info
+
+        if hasattr(processor.image_processor, "patch_size"):
+            image_patch_size = processor.image_processor.patch_size
+        else:
+            image_patch_size = DEFAULT_PATCH_SIZE
+        images, videos = qwen_process_vision_info(prompt, image_patch_size=image_patch_size)
+    except Exception:
+        # Fallback: generic extraction for non-Qwen models
+        images = _extract_images_from_messages(prompt) or None
+        videos = None
+
+    return {"images": images, "videos": videos}


 def encode_image_for_rollout_engine(image) -> str:
diff --git a/slime_plugins/megatron_bridge/glm4v_moe.py b/slime_plugins/megatron_bridge/glm4v_moe.py
index c213096a8..785276e97 100644
--- a/slime_plugins/megatron_bridge/glm4v_moe.py
+++ b/slime_plugins/megatron_bridge/glm4v_moe.py
@@ -103,6 +103,70 @@ def _gather_input_ids_from_cp(
     return torch.cat(whole_list).unsqueeze(0)  # [1, T_global]


+def _select_local_image_embeds(
+    full_input_ids: torch.Tensor,
+    cu_seqlens: torch.Tensor,
+    image_token_id: int,
+    image_embeds: torch.Tensor,
+    cp_rank: int,
+    cp_size: int,
+) -> torch.Tensor:
+    """Select the subset of *image_embeds* that falls in this CP rank's chunk.
+
+    With zigzag CP, each rank holds specific chunks of each packed sequence.
+    The vision encoder produces embeddings for ALL image tokens (ordered by
+    position in the full sequence).  This function returns only the embeddings
+    whose positions land in the local chunk.
+
+    Args:
+        full_input_ids: Reconstructed full input_ids [1, T_global].
+        cu_seqlens: **Global** cumulative sequence lengths.
+        image_token_id: Token id for image placeholder tokens.
+        image_embeds: Vision embeddings [N_total, hidden] for all image tokens.
+        cp_rank: This rank's position in the CP group.
+        cp_size: Total number of CP ranks.
+
+    Returns:
+        Subset of image_embeds [N_local, hidden] for this rank's image tokens.
+    """
+    device = full_input_ids.device
+    full_flat = full_input_ids[0]  # [T_global]
+    full_mask = full_flat == image_token_id
+
+    # Build boolean mask over T_global marking this rank's positions
+    T_global = full_flat.shape[0]
+    rank_mask = torch.zeros(T_global, dtype=torch.bool, device=device)
+
+    num_seqs = len(cu_seqlens) - 1
+    for i in range(num_seqs):
+        seq_start = cu_seqlens[i].item()
+        seqlen = (cu_seqlens[i + 1] - cu_seqlens[i]).item()
+        chunk_size = seqlen // (2 * cp_size)
+
+        # First-half chunk for this rank
+        first_start = seq_start + cp_rank * chunk_size
+        rank_mask[first_start : first_start + chunk_size] = True
+
+        # Second-half chunk for this rank (reversed order)
+        second_end = seq_start + seqlen - cp_rank * chunk_size
+        rank_mask[second_end - chunk_size : second_end] = True
+
+    # Image tokens that belong to this rank
+    local_image_mask = full_mask & rank_mask
+    n_local = local_image_mask.sum().item()
+
+    if n_local == 0:
+        return image_embeds[:0]  # empty slice preserving hidden dim
+    if n_local == image_embeds.shape[0]:
+        return image_embeds  # all image tokens are on this rank
+
+    # Map positions to indices in image_embeds via cumulative sum
+    image_cumsum = full_mask.long().cumsum(0)  # 1-indexed
+    local_positions = local_image_mask.nonzero(as_tuple=True)[0]
+    embed_indices = image_cumsum[local_positions] - 1
+    return image_embeds[embed_indices]
+
+
 # ---------------------------------------------------------------------------
 # Megatron VL Model
 # ---------------------------------------------------------------------------
@@ -138,6 +202,9 @@ def __init__(
             from transformers.models.glm4v_moe.modeling_glm4v_moe import Glm4vMoeVisionModel

             self.vision_model = Glm4vMoeVisionModel._from_config(hf_vision_config)
+            # Freeze vision encoder — not trained during RL
+            self.vision_model.requires_grad_(False)
+            self.vision_model.eval()
             hook_hf_module_setattr_for_tp_grad_sync(self.vision_model)
             if torch.cuda.is_available():
                 self.vision_model = self.vision_model.to("cuda")
@@ -180,8 +247,8 @@ def set_input_tensor(self, input_tensor):
     def _get_image_features(self, pixel_values, image_grid_thw):
         """Run HF vision encoder and return flat image embeddings."""
         pixel_values = pixel_values.to(dtype=self.vision_model.dtype)
-        vision_out = self.vision_model(pixel_values, grid_thw=image_grid_thw, return_dict=True)
-        return vision_out.pooler_output  # [total_image_tokens, hidden]
+        with torch.no_grad():
+            return self.vision_model(pixel_values, grid_thw=image_grid_thw)

     # -- M-RoPE position IDs -----------------------------------------------

@@ -294,6 +361,17 @@ def forward(
         assert pixel_values_videos is None, "Video not supported yet"
         assert inference_params is None, "Inference not supported"

+        # -- Extract cu_seqlens and CP info early (needed for both vision scatter and M-RoPE) --
+        cu_seqlens = None
+        if packed_seq_params is not None:
+            cu_seqlens = (
+                packed_seq_params.cu_seqlens_q_padded
+                if packed_seq_params.cu_seqlens_q_padded is not None
+                else packed_seq_params.cu_seqlens_q
+            )
+        cp_size = parallel_state.get_context_parallel_world_size()
+        full_input_ids = None  # cached for reuse between vision scatter and M-RoPE
+
         combined_embeddings = None

         if self.pre_process:
@@ -308,10 +386,26 @@ def forward(
                 image_embeds = self._get_image_features(pixel_values, image_grid_thw)
                 image_embeds = image_embeds.to(combined_embeddings.device, combined_embeddings.dtype)

+                # With CP > 1, input_ids is a local chunk but pixel_values
+                # cover ALL images.  Select only the embeddings whose tokens
+                # land in this rank's zigzag portion.
+                if cp_size > 1 and cu_seqlens is not None:
+                    full_input_ids = _gather_input_ids_from_cp(input_ids, cu_seqlens)
+                    cp_rank = parallel_state.get_context_parallel_rank()
+                    image_embeds = _select_local_image_embeds(
+                        full_input_ids,
+                        cu_seqlens,
+                        self.image_token_id,
+                        image_embeds,
+                        cp_rank,
+                        cp_size,
+                    )
+
                 image_mask = (input_ids == self.image_token_id).contiguous()
                 # Scatter: [seq, bs, hidden] → [bs, seq, hidden]
                 combined_embeddings = combined_embeddings.transpose(0, 1).contiguous()
-                combined_embeddings[image_mask] = image_embeds
+                if image_mask.any():
+                    combined_embeddings[image_mask] = image_embeds
                 combined_embeddings = combined_embeddings.transpose(0, 1).contiguous()

             # Scatter to sequence-parallel region if needed
@@ -325,17 +419,6 @@ def forward(
         pp_size = parallel_state.get_pipeline_model_parallel_world_size()

         if position_ids is None:
-            # Determine cu_seqlens for THD unpacking
-            cu_seqlens = None
-            if packed_seq_params is not None:
-                cu_seqlens = (
-                    packed_seq_params.cu_seqlens_q_padded
-                    if packed_seq_params.cu_seqlens_q_padded is not None
-                    else packed_seq_params.cu_seqlens_q
-                )
-
-            cp_size = parallel_state.get_context_parallel_world_size()
-
             if self.pre_process:
                 # First PP stage: compute position_ids from input_ids.
                 # With CP > 1, input_ids is a local chunk; reconstruct full
@@ -343,7 +426,8 @@ def forward(
                 # (image token positions affect the M-RoPE IDs).
                 if cu_seqlens is not None:
                     if cp_size > 1:
-                        full_input_ids = _gather_input_ids_from_cp(input_ids, cu_seqlens)
+                        if full_input_ids is None:
+                            full_input_ids = _gather_input_ids_from_cp(input_ids, cu_seqlens)
                     else:
                         full_input_ids = input_ids
                     input_ids_bshd = _thd_to_bshd(full_input_ids, cu_seqlens)

PATCH

echo "Patch applied successfully."
