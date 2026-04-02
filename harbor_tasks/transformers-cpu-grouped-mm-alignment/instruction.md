# Bug: MoE models crash on CPU with `torch.grouped_mm` due to tensor alignment

## Summary

When loading Mixture-of-Experts (MoE) models on CPU and running inference, `torch.grouped_mm` (or `torch._grouped_mm`) crashes with a segfault or alignment error. This happens because tensors loaded via memory-mapped safetensors files are not guaranteed to be 16-byte aligned, and the CPU implementation of `grouped_mm` (before PyTorch 2.11) requires 16-byte alignment for TMA/SIMD operations.

## Context

The codebase currently attempts to solve alignment issues during weight loading by cloning misaligned tensors as a conversion operation (`Force16BytesAlignment` in `src/transformers/core_model_loading.py`). This approach is applied in `src/transformers/conversion_mapping.py` for several MoE architectures (e.g., `qwen3_moe`, `mixtral`, `minimax_m2`).

However, this weight-conversion approach has fundamental limitations:
- It doesn't cover all loading paths (e.g., memory-mapped/lazy loading from safetensors)
- It can't handle tensors created after dequantization
- It adds unnecessary complexity to the weight conversion pipeline

## Reproduction

The crash occurs specifically when:
1. A MoE model is loaded on CPU
2. The loaded expert weight tensors happen to be misaligned (e.g., via safetensors mmap)
3. The code path reaches `torch.grouped_mm` / `torch._grouped_mm`

The relevant function that decides whether to use `grouped_mm` is `_can_use_grouped_mm` in `src/transformers/integrations/moe.py`. Currently, it only checks for `torch.compile` dtype limitations but does not check for CPU alignment issues.

## Expected behavior

The code should detect when CPU tensors are misaligned and fall back to the non-`grouped_mm` path instead of crashing. The fragile weight-conversion-time alignment enforcement should be replaced with a robust runtime check.

## Relevant files

- `src/transformers/integrations/moe.py` — `_can_use_grouped_mm()` function
- `src/transformers/core_model_loading.py` — `Force16BytesAlignment` class
- `src/transformers/conversion_mapping.py` — uses of `Force16BytesAlignment` in weight converters
- `docs/source/en/weightconverter.md` — documentation for `Force16BytesAlignment`
- `tests/vlm_tester.py` — test helper with `intermediate_size` that may trigger alignment issues
