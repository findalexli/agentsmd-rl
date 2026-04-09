# [NPU] Fix Qwen3.5 Video Processor for NPU Compatibility

## Problem

The Qwen3VLVideoProcessor fails on NPU hardware when processing video inputs. The issue is that the processor performs a tensor permutation operation with more than 8 dimensions, which is not supported on NPU devices.

When attempting to process videos with Qwen3.5 models on NPU, the execution fails with dimension-related errors during the preprocessing stage.

## Expected Behavior

Video processing should work correctly on NPU hardware. The fix should:
1. Avoid performing permute operations with more than 8 dimensions
2. Decompose any >8D permute into a sequence of <=8D permutes
3. Maintain mathematical equivalence with the original transformation
4. Apply to both the existing Qwen2VL image processor and the new Qwen3VL video processor

## Files to Look At

- `python/sglang/srt/hardware_backend/npu/modules/qwen_vl_processor.py` — Contains the NPU-specific patches for Qwen VL processors. The `npu_wrapper_preprocess` function handles image preprocessing, and you'll need to add similar handling for video preprocessing.

## Key Context

The existing `npu_wrapper_preprocess` function in this file already applies a similar fix for the Qwen2VL image processor (following PR #20189). You need to extend this pattern to also support the Qwen3VL video processor.

The fix involves:
1. Extracting the patch transformation logic into a reusable helper function
2. Creating a new wrapper for Qwen3VLVideoProcessor that uses this helper
3. Registering the new wrapper in the patch application function

## Hints

- Look at how the existing image processor patch avoids >8D permutes
- The video processor will need similar dimension handling
- Consider creating a shared helper function for the transformation
- The fix should be registered for `transformers.models.qwen3_vl.video_processing_qwen3_vl.Qwen3VLVideoProcessor`
