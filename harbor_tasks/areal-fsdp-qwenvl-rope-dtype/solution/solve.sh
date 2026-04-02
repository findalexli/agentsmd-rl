#!/usr/bin/env bash
set -euo pipefail

FILE="areal/engine/fsdp_engine.py"

# Idempotency: check if already fixed (keyword args in get_rope_index call)
if grep -q 'input_ids=input_ids,' "$FILE"; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/engine/fsdp_engine.py b/areal/engine/fsdp_engine.py
index 151020f8b..40b8e545a 100644
--- a/areal/engine/fsdp_engine.py
+++ b/areal/engine/fsdp_engine.py
@@ -1311,6 +1311,13 @@ def _prepare_mb_list(self, input_: dict[str, Any]) -> MicroBatchList:
         if is_qwen_vl_model(self.model_config.model_type):
             attn_mask = input_["attention_mask"]
             input_ids = input_["input_ids"]
+            # NOTE: Qwen-VL get_rope_index performs indexed assignment where
+            # source positions are int64 and position_ids inherits input_ids.dtype.
+            # Ensure input_ids uses int64 so destination/source dtypes align and
+            # avoid "Index put requires the source and destination dtypes match".
+            if input_ids.dtype != torch.long:
+                input_ids = input_ids.to(torch.long)
+                input_["input_ids"] = input_ids
             image_grid_thw = None
             video_grid_thw = None
             if "multi_modal_input" in input_:
@@ -1331,7 +1338,10 @@ def _prepare_mb_list(self, input_: dict[str, Any]) -> MicroBatchList:
                     video_grid_thw = torch.cat(video_grid_thw_list)

             position_ids, _ = self.model.model.get_rope_index(
-                input_ids, image_grid_thw, video_grid_thw, attn_mask
+                input_ids=input_ids,
+                image_grid_thw=image_grid_thw,
+                video_grid_thw=video_grid_thw,
+                attention_mask=attn_mask,
             )
             position_ids = torch.einsum("ijk->jki", position_ids)
             input_["position_ids"] = position_ids

PATCH

echo "Patch applied successfully."
