#!/usr/bin/env bash
# Gold solution for huggingface/transformers#45185.
# Idempotent: applies the gold patch only if not already applied.
set -euo pipefail

cd /workspace/transformers

# Idempotency guard: a distinctive line introduced by the patch.
if grep -q 'A tensor of shape `(bs, len)` assigning each token to a vision group' \
        src/transformers/models/gemma3/modeling_gemma3.py 2>/dev/null; then
    echo "Patch already applied; nothing to do."
    exit 0
fi

# The gold patch is inlined below (HEREDOC, single-quoted to disable expansion).
# It is the diff captured from the merged PR.
patch -p1 <<'PATCH'
diff --git a/src/transformers/models/gemma3/modeling_gemma3.py b/src/transformers/models/gemma3/modeling_gemma3.py
index 23607505156f..0dd41d6fd450 100644
--- a/src/transformers/models/gemma3/modeling_gemma3.py
+++ b/src/transformers/models/gemma3/modeling_gemma3.py
@@ -704,42 +704,29 @@ def forward(self, vision_outputs: torch.Tensor):
         return projected_vision_outputs.type_as(vision_outputs)


-def token_type_ids_mask_function(
-    token_type_ids: torch.Tensor | None,
-    image_group_ids: torch.Tensor | None,
-) -> Callable | None:
+def token_type_ids_mask_function(group_ids: torch.Tensor) -> Callable:
     """
     This function adds the correct offsets to the `q_idx` and `kv_idx` as the torch API can only accept lengths,
     not start and end indices.
+    Args:
+        group_ids (`torch.Tensor`):
+            A tensor of shape `(bs, len)` assigning each token to a vision group. Tokens with the same group
+            come from the same input image. Text is denoted by `-1`.
     """
-    # Do not return an additional mask in this case
-    if token_type_ids is None:
-        return None

     def inner_mask(batch_idx: int, head_idx: int, q_idx: int, kv_idx: int) -> bool:
-        # If it's 1 for both query and key/value, we are in an image block
-        # NOTE: static cache shape goes beyond input seq length, while token_type_ids.shape[1] == input seq length
-        # Since vmap doesn't support `if statement` we workaround it with `torch.where`
-        safe_q_idx = torch.where(q_idx < token_type_ids.shape[1], q_idx, 0)
-        safe_kv_idx = torch.where(kv_idx < token_type_ids.shape[1], kv_idx, 0)
-
-        token_type_ids_at_q_idx = token_type_ids[batch_idx, safe_q_idx]
-        token_type_ids_at_q_idx = torch.where(q_idx < token_type_ids.shape[1], token_type_ids_at_q_idx, 0)
-
-        token_type_ids_at_kv_idx = token_type_ids[batch_idx, safe_kv_idx]
-        token_type_ids_at_kv_idx = torch.where(kv_idx < token_type_ids.shape[1], token_type_ids_at_kv_idx, 0)
+        seq_length = group_ids.shape[-1]

-        image_group_ids_at_q_idx = image_group_ids[batch_idx, safe_q_idx]
-        image_group_ids_at_q_idx = torch.where(q_idx < image_group_ids.shape[1], image_group_ids_at_q_idx, -1)
+        # clamp indices because with static cache they can go beyond `group_ids.shape[-1]`
+        q_idx_clamped = q_idx.clamp(max=seq_length - 1)
+        kv_idx_clamped = kv_idx.clamp(max=seq_length - 1)

-        image_group_ids_at_kv_idx = image_group_ids[batch_idx, safe_kv_idx]
-        image_group_ids_at_kv_idx = torch.where(kv_idx < image_group_ids.shape[1], image_group_ids_at_kv_idx, -1)
-
-        is_image_block = (token_type_ids_at_q_idx == 1) & (token_type_ids_at_kv_idx == 1)
-        same_image_block = image_group_ids_at_q_idx == image_group_ids_at_kv_idx
-
-        # This is bidirectional attention whenever we are dealing with image tokens
-        return is_image_block & same_image_block
+        # Unmask if the q and kv come from same group which is not -1 (i.e. non-text)
+        q_group = group_ids[batch_idx, q_idx_clamped]
+        kv_group = group_ids[batch_idx, kv_idx_clamped]
+        q_group = torch.where(q_idx < seq_length, q_group, -1)
+        kv_group = torch.where(kv_idx < seq_length, kv_group, -1)
+        return (q_group == kv_group) & (q_group >= 0)

     return inner_mask

@@ -790,11 +777,9 @@ def create_causal_mask_mapping(
         is_image = (token_type_ids == 1).to(inputs_embeds.device)
         is_previous_image = nn.functional.pad(is_image, (1, 0), value=0)[:, :-1]
         new_image_start = is_image & ~is_previous_image
-        image_group_ids = torch.cumsum(new_image_start.int(), dim=1) - 1
-        image_group_ids = torch.where(is_image, image_group_ids, -1)
-        mask_kwargs["or_mask_function"] = token_type_ids_mask_function(
-            token_type_ids.to(inputs_embeds.device), image_group_ids
-        )
+        group_ids = torch.cumsum(new_image_start.int(), dim=1) - 1
+        group_ids = torch.where(is_image, group_ids, -1)
+        mask_kwargs["or_mask_function"] = token_type_ids_mask_function(group_ids)

     return create_masks_for_generate(**mask_kwargs)

diff --git a/src/transformers/models/gemma3/modular_gemma3.py b/src/transformers/models/gemma3/modular_gemma3.py
index b87d0d206631..fe8678265ead 100644
--- a/src/transformers/models/gemma3/modular_gemma3.py
+++ b/src/transformers/models/gemma3/modular_gemma3.py
@@ -650,11 +650,9 @@ def create_causal_mask_mapping(
         is_image = (token_type_ids == 1).to(inputs_embeds.device)
         is_previous_image = nn.functional.pad(is_image, (1, 0), value=0)[:, :-1]
         new_image_start = is_image & ~is_previous_image
-        image_group_ids = torch.cumsum(new_image_start.int(), dim=1) - 1
-        image_group_ids = torch.where(is_image, image_group_ids, -1)
-        mask_kwargs["or_mask_function"] = token_type_ids_mask_function(
-            token_type_ids.to(inputs_embeds.device), image_group_ids
-        )
+        group_ids = torch.cumsum(new_image_start.int(), dim=1) - 1
+        group_ids = torch.where(is_image, group_ids, -1)
+        mask_kwargs["or_mask_function"] = token_type_ids_mask_function(group_ids)

     return create_masks_for_generate(**mask_kwargs)

diff --git a/src/transformers/models/git/modeling_git.py b/src/transformers/models/git/modeling_git.py
index f0c9919e8184..507aa4f0ad31 100644
--- a/src/transformers/models/git/modeling_git.py
+++ b/src/transformers/models/git/modeling_git.py
@@ -73,42 +73,29 @@ class GitVisionModelOutput(ModelOutput):


 # Copied from transformers.models.gemma3.modeling_gemma3.token_type_ids_mask_function
-def token_type_ids_mask_function(
-    token_type_ids: torch.Tensor | None,
-    image_group_ids: torch.Tensor | None,
-) -> Callable | None:
+def token_type_ids_mask_function(group_ids: torch.Tensor) -> Callable:
     """
     This function adds the correct offsets to the `q_idx` and `kv_idx` as the torch API can only accept lengths,
     not start and end indices.
+    Args:
+        group_ids (`torch.Tensor`):
+            A tensor of shape `(bs, len)` assigning each token to a vision group. Tokens with the same group
+            come from the same input image. Text is denoted by `-1`.
     """
-    # Do not return an additional mask in this case
-    if token_type_ids is None:
-        return None

     def inner_mask(batch_idx: int, head_idx: int, q_idx: int, kv_idx: int) -> bool:
-        # If it's 1 for both query and key/value, we are in an image block
-        # NOTE: static cache shape goes beyond input seq length, while token_type_ids.shape[1] == input seq length
-        # Since vmap doesn't support `if statement` we workaround it with `torch.where`
-        safe_q_idx = torch.where(q_idx < token_type_ids.shape[1], q_idx, 0)
-        safe_kv_idx = torch.where(kv_idx < token_type_ids.shape[1], kv_idx, 0)
-
-        token_type_ids_at_q_idx = token_type_ids[batch_idx, safe_q_idx]
-        token_type_ids_at_q_idx = torch.where(q_idx < token_type_ids.shape[1], token_type_ids_at_q_idx, 0)
-
-        token_type_ids_at_kv_idx = token_type_ids[batch_idx, safe_kv_idx]
-        token_type_ids_at_kv_idx = torch.where(kv_idx < token_type_ids.shape[1], token_type_ids_at_kv_idx, 0)
+        seq_length = group_ids.shape[-1]

-        image_group_ids_at_q_idx = image_group_ids[batch_idx, safe_q_idx]
-        image_group_ids_at_q_idx = torch.where(q_idx < image_group_ids.shape[1], image_group_ids_at_q_idx, -1)
+        # clamp indices because with static cache they can go beyond `group_ids.shape[-1]`
+        q_idx_clamped = q_idx.clamp(max=seq_length - 1)
+        kv_idx_clamped = kv_idx.clamp(max=seq_length - 1)

-        image_group_ids_at_kv_idx = image_group_ids[batch_idx, safe_kv_idx]
-        image_group_ids_at_kv_idx = torch.where(kv_idx < image_group_ids.shape[1], image_group_ids_at_kv_idx, -1)
-
-        is_image_block = (token_type_ids_at_q_idx == 1) & (token_type_ids_at_kv_idx == 1)
-        same_image_block = image_group_ids_at_q_idx == image_group_ids_at_kv_idx
-
-        # This is bidirectional attention whenever we are dealing with image tokens
-        return is_image_block & same_image_block
+        # Unmask if the q and kv come from same group which is not -1 (i.e. non-text)
+        q_group = group_ids[batch_idx, q_idx_clamped]
+        kv_group = group_ids[batch_idx, kv_idx_clamped]
+        q_group = torch.where(q_idx < seq_length, q_group, -1)
+        kv_group = torch.where(kv_idx < seq_length, kv_group, -1)
+        return (q_group == kv_group) & (q_group >= 0)

     return inner_mask

@@ -160,11 +147,9 @@ def create_causal_mask_mapping(
         is_image = (token_type_ids == 1).to(inputs_embeds.device)
         is_previous_image = nn.functional.pad(is_image, (1, 0), value=0)[:, :-1]
         new_image_start = is_image & ~is_previous_image
-        image_group_ids = torch.cumsum(new_image_start.int(), dim=1) - 1
-        image_group_ids = torch.where(is_image, image_group_ids, -1)
-        mask_kwargs["or_mask_function"] = token_type_ids_mask_function(
-            token_type_ids.to(inputs_embeds.device), image_group_ids
-        )
+        group_ids = torch.cumsum(new_image_start.int(), dim=1) - 1
+        group_ids = torch.where(is_image, group_ids, -1)
+        mask_kwargs["or_mask_function"] = token_type_ids_mask_function(group_ids)

     return create_masks_for_generate(**mask_kwargs)

diff --git a/src/transformers/models/paligemma/modeling_paligemma.py b/src/transformers/models/paligemma/modeling_paligemma.py
index 2505aecae52f..369514a55f76 100644
--- a/src/transformers/models/paligemma/modeling_paligemma.py
+++ b/src/transformers/models/paligemma/modeling_paligemma.py
@@ -100,42 +100,29 @@ def forward(self, image_features):
         return hidden_states


-def token_type_ids_mask_function(
-    token_type_ids: torch.Tensor | None,
-    image_group_ids: torch.Tensor | None,
-) -> Callable | None:
+def token_type_ids_mask_function(group_ids: torch.Tensor) -> Callable:
     """
     This function adds the correct offsets to the `q_idx` and `kv_idx` as the torch API can only accept lengths,
     not start and end indices.
+    Args:
+        group_ids (`torch.Tensor`):
+            A tensor of shape `(bs, len)` assigning each token to a vision group. Tokens with the same group
+            come from the same input image. Text is denoted by `-1`.
     """
-    # Do not return an additional mask in this case
-    if token_type_ids is None:
-        return None

     def inner_mask(batch_idx: int, head_idx: int, q_idx: int, kv_idx: int) -> bool:
-        # If it's 1 for both query and key/value, we are in an image block
-        # NOTE: static cache shape goes beyond input seq length, while token_type_ids.shape[1] == input seq length
-        # Since vmap doesn't support `if statement` we workaround it with `torch.where`
-        safe_q_idx = torch.where(q_idx < token_type_ids.shape[1], q_idx, 0)
-        safe_kv_idx = torch.where(kv_idx < token_type_ids.shape[1], kv_idx, 0)
+        seq_length = group_ids.shape[-1]

-        token_type_ids_at_q_idx = token_type_ids[batch_idx, safe_q_idx]
-        token_type_ids_at_q_idx = torch.where(q_idx < token_type_ids.shape[1], token_type_ids_at_q_idx, 0)
+        # clamp indices because with static cache they can go beyond `group_ids.shape[-1]`
+        q_idx_clamped = q_idx.clamp(max=seq_length - 1)
+        kv_idx_clamped = kv_idx.clamp(max=seq_length - 1)

-        token_type_ids_at_kv_idx = token_type_ids[batch_idx, safe_kv_idx]
-        token_type_ids_at_kv_idx = torch.where(kv_idx < token_type_ids.shape[1], token_type_ids_at_kv_idx, 0)
-
-        image_group_ids_at_q_idx = image_group_ids[batch_idx, safe_q_idx]
-        image_group_ids_at_q_idx = torch.where(q_idx < image_group_ids.shape[1], image_group_ids_at_q_idx, -1)
-
-        image_group_ids_at_kv_idx = image_group_ids[batch_idx, safe_kv_idx]
-        image_group_ids_at_kv_idx = torch.where(kv_idx < image_group_ids.shape[1], image_group_ids_at_kv_idx, -1)
-
-        is_image_block = (token_type_ids_at_q_idx == 1) & (token_type_ids_at_kv_idx == 1)
-        same_image_block = image_group_ids_at_q_idx == image_group_ids_at_kv_idx
-
-        # This is bidirectional attention whenever we are dealing with image tokens
-        return is_image_block & same_image_block
+        # Unmask if the q and kv come from same group which is not -1 (i.e. non-text)
+        q_group = group_ids[batch_idx, q_idx_clamped]
+        kv_group = group_ids[batch_idx, kv_idx_clamped]
+        q_group = torch.where(q_idx < seq_length, q_group, -1)
+        kv_group = torch.where(kv_idx < seq_length, kv_group, -1)
+        return (q_group == kv_group) & (q_group >= 0)

     return inner_mask

@@ -204,11 +191,9 @@ def create_causal_mask_mapping(
         is_image = (token_type_ids == 1).to(inputs_embeds.device)
         is_previous_image = nn.functional.pad(is_image, (1, 0), value=0)[:, :-1]
         new_image_start = is_image & ~is_previous_image
-        image_group_ids = torch.cumsum(new_image_start.int(), dim=1) - 1
-        image_group_ids = torch.where(is_image, image_group_ids, torch.full_like(token_type_ids, -1))
-        mask_kwargs["or_mask_function"] = token_type_ids_mask_function(
-            token_type_ids.to(inputs_embeds.device), image_group_ids
-        )
+        group_ids = torch.cumsum(new_image_start.int(), dim=1) - 1
+        group_ids = torch.where(is_image, group_ids, torch.full_like(token_type_ids, -1))
+        mask_kwargs["or_mask_function"] = token_type_ids_mask_function(group_ids)

     return create_masks_for_generate(**mask_kwargs)
PATCH

echo "Patch applied successfully."
