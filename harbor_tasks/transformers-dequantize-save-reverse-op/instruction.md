# Bug: `save_pretrained()` crashes for dequantized models

## Summary

When a quantized model is loaded with `dequantize=True` (e.g., using `Mxfp4Config`, `FineGrainedFP8Config`, or `MetalConfig`), calling `save_pretrained()` on it raises a `NotImplementedError`.

## Reproduction

Load any quantized model with `dequantize=True`, then try to save it:

```python
from transformers import AutoModelForCausalLM, FineGrainedFP8Config

config = FineGrainedFP8Config(dequantize=True)
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B-FP8", quantization_config=config)
model.save_pretrained("/tmp/saved_model")
# => NotImplementedError
```

The same crash occurs with `Mxfp4Config(dequantize=True)` and `MetalConfig(dequantize=True)`.

## Root Cause

The `save_pretrained` flow calls `reverse_op` on each weight conversion operation to undo the loading transformation before saving. The base `ConversionOps` class in `src/transformers/core_model_loading.py` defines `reverse_op` as raising `NotImplementedError`.

The dequantize operation classes (`Fp8Dequantize` in `src/transformers/integrations/finegrained_fp8.py`, `MetalDequantize` in `src/transformers/integrations/metal_quantization.py`, and `Mxfp4Dequantize` in `src/transformers/integrations/mxfp4.py`) do not override this property.

Since dequantized weights are already in their target dtype, the reverse operation should simply pass the weights through without any conversion.

## Expected Behavior

`save_pretrained()` should succeed for dequantized models. The saved weights should be the dequantized values as-is, and the saved `config.json` should not contain a `quantization_config` key.

## Files to Investigate

- `src/transformers/core_model_loading.py` — `ConversionOps` base class and `reverse_op` property
- `src/transformers/integrations/finegrained_fp8.py` — `Fp8Dequantize` class
- `src/transformers/integrations/metal_quantization.py` — `MetalDequantize` class
- `src/transformers/integrations/mxfp4.py` — `Mxfp4Dequantize` class
