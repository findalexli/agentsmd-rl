#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied (check for the new function)
if grep -q 'def transform_patches_to_flatten' python/sglang/srt/hardware_backend/npu/modules/qwen_vl_processor.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply - <<'PATCH'
diff --git a/python/sglang/srt/hardware_backend/npu/modules/qwen_vl_processor.py b/python/sglang/srt/hardware_backend/npu/modules/qwen_vl_processor.py
index 1b3cf8b5ae67..e761bf1b4a81 100644
--- a/python/sglang/srt/hardware_backend/npu/modules/qwen_vl_processor.py
+++ b/python/sglang/srt/hardware_backend/npu/modules/qwen_vl_processor.py
@@ -7,13 +7,62 @@ from transformers.models.qwen2_vl.image_processing_qwen2_vl_fast import (
     group_images_by_shape,
     reorder_images,
 )
-from transformers.image_utils import SizeDict
+from transformers.image_utils import (
+    ChannelDimension,
+    PILImageResampling,
+    SizeDict,
+    get_image_size,
+)
 from transformers.models.qwen2_vl.image_processing_qwen2_vl import smart_resize
+from transformers.models.qwen3_vl.video_processing_qwen3_vl import (
+    smart_resize as smart_resize_video,
+)
 from transformers.utils import TensorType
+from transformers.video_utils import group_videos_by_shape, reorder_videos

 from sglang.srt.utils import apply_module_patch


+def transform_patches_to_flatten(
+    patches: torch.Tensor,
+    batch_size: int,
+    grid_t: int,
+    temporal_patch_size: int,
+    channel: int,
+    grid_h: int,
+    grid_w: int,
+    patch_size: int,
+    merge_size: int,
+) -> torch.Tensor:
+    patches = patches.view(
+        batch_size * grid_t,
+        temporal_patch_size * channel,
+        grid_h // merge_size,
+        merge_size,
+        patch_size,
+        grid_w // merge_size,
+        merge_size,
+        patch_size,
+    )
+    patches = patches.permute(0, 1, 2, 5, 3, 6, 4, 7)
+    patches = patches.reshape(
+        batch_size,
+        grid_t,
+        temporal_patch_size,
+        channel,
+        grid_h * grid_w,
+        patch_size,
+        patch_size,
+    )
+    patches = patches.permute(0, 1, 4, 3, 2, 5, 6)
+    flatten_patches = patches.reshape(
+        batch_size,
+        grid_t * grid_h * grid_w,
+        -1,
+    )
+    return flatten_patches
+
+
 # Func refers to transformers.models.qwen2_vl.image_processing_qwen2_vl_fast.py
 # Qwen2VLImageProcessorFast._preprocess
 def npu_wrapper_preprocess(func):
@@ -90,31 +139,16 @@ def npu_wrapper_preprocess(func):
             ######################################
             # Start of modifications for sglang  #
             ######################################
-            patches = patches.view(
-                batch_size * grid_t,
-                temporal_patch_size * channel,
-                grid_h // merge_size,
-                merge_size,
-                patch_size,
-                grid_w // merge_size,
-                merge_size,
-                patch_size,
-            )
-            patches = patches.permute(0, 1, 2, 5, 3, 6, 4, 7)
-            patches = patches.reshape(
+            flatten_patches = transform_patches_to_flatten(
+                patches,
                 batch_size,
                 grid_t,
                 temporal_patch_size,
                 channel,
-                grid_h * grid_w,
+                grid_h,
+                grid_w,
                 patch_size,
-                patch_size,
-            )
-            patches = patches.permute(0, 1, 4, 3, 2, 5, 6)
-            flatten_patches = patches.reshape(
-                batch_size,
-                grid_t * grid_h * grid_w,
-                -1,
+                merge_size,
             )
             ######################################
             #  End of modifications for sglang   #
@@ -138,6 +172,123 @@ def npu_wrapper_preprocess(func):
     return _preprocess


+# Func refers to transformers.models.qwen3_vl.video_processing_qwen3_vl.py
+# Qwen3VLVideoProcessorFast._preprocess
+def npu_wrapper_video_preprocess(func):
+
+    def _preprocess(
+        self,
+        videos: list[torch.Tensor],
+        do_convert_rgb: bool = True,
+        do_resize: bool = True,
+        size: SizeDict | None = None,
+        interpolation: PILImageResampling = PILImageResampling.BICUBIC,
+        do_rescale: bool = True,
+        rescale_factor: float = 1 / 255.0,
+        do_normalize: bool = True,
+        image_mean: float | list[float] | None = None,
+        image_std: float | list[float] | None = None,
+        patch_size: int | None = None,
+        temporal_patch_size: int | None = None,
+        merge_size: int | None = None,
+        return_tensors: str | TensorType | None = None,
+        **kwargs,
+    ):
+        grouped_videos, grouped_videos_index = group_videos_by_shape(videos)
+        resized_videos_grouped = {}
+
+        for shape, stacked_videos in grouped_videos.items():
+            B, T, C, H, W = stacked_videos.shape
+            num_frames, height, width = T, H, W
+            if do_resize:
+                resized_height, resized_width = smart_resize_video(
+                    num_frames=num_frames,
+                    height=height,
+                    width=width,
+                    temporal_factor=temporal_patch_size,
+                    factor=patch_size * merge_size,
+                    min_pixels=size.shortest_edge,
+                    max_pixels=size.longest_edge,
+                )
+                stacked_videos = stacked_videos.view(B * T, C, H, W)
+                stacked_videos = self.resize(
+                    stacked_videos,
+                    size=SizeDict(height=resized_height, width=resized_width),
+                    interpolation=interpolation,
+                )
+                stacked_videos = stacked_videos.view(
+                    B, T, C, resized_height, resized_width
+                )
+            resized_videos_grouped[shape] = stacked_videos
+        resized_videos = reorder_videos(resized_videos_grouped, grouped_videos_index)
+
+        # Group videos by size for further processing
+        # Needed in case do_resize is False, or resize returns videos with different sizes
+        grouped_videos, grouped_videos_index = group_videos_by_shape(resized_videos)
+        processed_videos_grouped = {}
+        processed_grids = {}
+        for shape, stacked_videos in grouped_videos.items():
+            resized_height, resized_width = get_image_size(
+                stacked_videos[0], channel_dim=ChannelDimension.FIRST
+            )
+
+            # Fused rescale and normalize
+            stacked_videos = self.rescale_and_normalize(
+                stacked_videos,
+                do_rescale,
+                rescale_factor,
+                do_normalize,
+                image_mean,
+                image_std,
+            )
+            patches = stacked_videos
+
+            # Check that videos have `num_frames` divisible by `temporal_patch_size`
+            T = patches.shape[1]
+            if pad := -T % temporal_patch_size:
+                repeats = patches[:, -1:].expand(-1, pad, -1, -1, -1)
+                patches = torch.cat((patches, repeats), dim=1)
+            batch_size, grid_t, channel = patches.shape[:3]
+            grid_t = grid_t // temporal_patch_size
+            grid_h, grid_w = resized_height // patch_size, resized_width // patch_size
+
+            ######################################
+            # Start of modifications for sglang  #
+            ######################################
+            flatten_patches = transform_patches_to_flatten(
+                patches,
+                batch_size,
+                grid_t,
+                temporal_patch_size,
+                channel,
+                grid_h,
+                grid_w,
+                patch_size,
+                merge_size,
+            )
+            ######################################
+            #  End of modifications for sglang   #
+            ######################################
+
+            processed_videos_grouped[shape] = flatten_patches
+            processed_grids[shape] = [[grid_t, grid_h, grid_w]] * batch_size
+
+        processed_videos = reorder_videos(
+            processed_videos_grouped, grouped_videos_index
+        )
+        processed_grids = reorder_videos(processed_grids, grouped_videos_index)
+        pixel_values_videos = torch.cat(processed_videos, dim=0)
+        video_grid_thw = torch.tensor(processed_grids)
+        data = {
+            "pixel_values_videos": pixel_values_videos,
+            "video_grid_thw": video_grid_thw,
+        }
+
+        return BatchFeature(data=data, tensor_type=return_tensors)
+
+    return _preprocess
+
+
 _npu_preprocess_patched = False


@@ -150,4 +301,9 @@ def npu_apply_qwen_image_preprocess_patch():
         "_preprocess",
         [npu_wrapper_preprocess],
     )
+    apply_module_patch(
+        "transformers.models.qwen3_vl.video_processing_qwen3_vl.Qwen3VLVideoProcessor",
+        "_preprocess",
+        [npu_wrapper_video_preprocess],
+    )
     _npu_preprocess_patched = True

PATCH

echo "Patch applied successfully."
