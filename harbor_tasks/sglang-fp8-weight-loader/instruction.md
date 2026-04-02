# Bug: FP8 quantized model fails to load weights for Qwen3-Next

## Summary

When loading FP8-quantized weights for the Qwen3-Next model family (e.g., `Qwen3-Coder-Next-FP8`), the server crashes with:

```
AttributeError: property 'weight_loader' of 'ModelWeightParameter' object has no setter
```

The crash occurs during model initialization in `python/sglang/srt/models/qwen3_next.py`, specifically in the `Qwen3GatedDeltaNet.__init__` method where weight loaders are overridden for packed checkpoint format.

## Details

The `Qwen3GatedDeltaNet` layer overrides the `weight_loader` on its `in_proj_qkvz` and `in_proj_ba` projection weights to handle the packed checkpoint format. This works fine for non-quantized models where `weight_loader` is a plain attribute on the parameter object.

However, when quantization is enabled (e.g., FP8), the weight parameters are `ModelWeightParameter` instances from vLLM's quantization layer. In `ModelWeightParameter`, `weight_loader` is implemented as a **read-only property** (with only a getter, no setter) that delegates to an internal attribute. Direct assignment to this property raises `AttributeError`.

## Reproduction

Load any FP8-quantized Qwen3-Next variant with tensor parallelism:

```
python -m sglang.launch_server --model-path Qwen/Qwen3-Coder-Next-FP8 --tp 2
```

The crash happens immediately during model construction, before any inference begins.

## Files to investigate

- `python/sglang/srt/models/qwen3_next.py` — the `Qwen3GatedDeltaNet.__init__` method, around the weight loader override section
