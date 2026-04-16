# Bug: MoE models crash on CPU with `torch.grouped_mm` due to tensor alignment

## Summary

When running Mixture-of-Experts (MoE) models on CPU, `torch.grouped_mm` (or `torch._grouped_mm`) can crash with a segfault or alignment error. Tensors loaded via memory-mapped safetensors files are not guaranteed to be 16-byte aligned, and the CPU implementation of `grouped_mm` in PyTorch versions 2.10.0 and earlier requires 16-byte alignment for TMA/SIMD operations. PyTorch 2.11 and later fixed this upstream (see pytorch/pytorch#172440).

## Reproduction

The crash occurs when:
1. A MoE model is loaded on CPU
2. Expert weight tensors happen to be misaligned (data pointer not divisible by 16), which commonly occurs with safetensors mmap loading
3. The code path reaches `torch.grouped_mm` / `torch._grouped_mm`

## Current behavior

The function `_can_use_grouped_mm(input, weight, offs)` in `transformers.integrations.moe` decides whether to use `grouped_mm`. Currently it only checks for `torch.compile` dtype limitations but does not verify CPU tensor alignment, allowing misaligned tensors through to `grouped_mm` which then crashes.

The codebase also includes a `Force16BytesAlignment` conversion operation that attempts to fix alignment at weight-loading time via the conversion mapping system. This approach is fragile — it doesn't cover all loading paths (e.g., lazy/memory-mapped safetensors loading) and can't handle tensors created after dequantization.

## Expected behavior

1. **Runtime alignment check**: `_can_use_grouped_mm(input, weight, offs)` should return `False` when running on CPU with PyTorch <= 2.10.0 and either the `input` or `weight` tensor's data pointer is not 16-byte aligned (`data_ptr() % 16 != 0`). This causes a fallback to the safe non-`grouped_mm` path instead of crashing. For properly aligned tensors (when `grouped_mm` is available), it should continue to return `True`. When `grouped_mm` is not available at all, it should return `False` as before.

2. **Remove `Force16BytesAlignment` from conversion mappings**: With a runtime alignment check in place, the `Force16BytesAlignment` workaround in the weight conversion pipeline is unnecessary. `_build_checkpoint_conversion_mapping()` in `transformers.conversion_mapping` should not include any `Force16BytesAlignment` operations in its converter entries. The mapping must still build successfully and include MoE model entries such as `mixtral` and `qwen3_moe`.

3. **Code quality**: All modified files must pass `ruff check` and `ruff format --check`.
