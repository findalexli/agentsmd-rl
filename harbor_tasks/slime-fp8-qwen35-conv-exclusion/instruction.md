# FP8 conversion crashes or corrupts Qwen3.5 models with Mamba-style layers

## Summary

The `tools/convert_hf_to_fp8.py` script converts HuggingFace model weights to FP8 format for efficient inference. It has an exclusion list of weight keys that should **not** be quantized (e.g., layernorms, embeddings, routing weights). However, models that contain Mamba-style layers — such as Qwen3.5 — have additional weight types that are incompatible with FP8 quantization but are not currently excluded.

## Reproduction

When running the FP8 conversion on a Qwen3.5 model (or any model with Mamba/state-space layers), certain architecture-specific weight types unique to these layers get incorrectly quantized. This can result in corrupted model outputs or runtime errors during inference.

## Relevant code

- `tools/convert_hf_to_fp8.py`, specifically the `process_file()` function
- Look at the conditional block (around line 130) that decides which weight keys to quantize vs. skip

## Expected behavior

The exclusion filter in `process_file()` should recognize and skip all weight types that are not suitable for FP8 quantization, including those specific to Mamba/state-space architectures.
