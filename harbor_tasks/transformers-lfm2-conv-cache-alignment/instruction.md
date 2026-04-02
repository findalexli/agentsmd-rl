# LFM2 Hybrid Conv Cache: Incorrect Prefill/Decode State Detection

## Bug Description

The `Lfm2HybridConvCache` class in `src/transformers/models/lfm2/` (and correspondingly in `lfm2_moe`) has a fragile mechanism for deciding whether conv layers should run in "prefill" mode (first pass) vs "decode" mode (subsequent tokens).

Currently, the conv module's `slow_forward` and `cuda_kernels_forward` methods compute a `past_seen_tokens` value from the cache's `get_seq_length()` method, then apply a correction by subtracting `seqlen` if a `full_attention` layer appears before the current conv layer in the layer ordering. This correction is needed because the attention layer may have already appended to the KV cache, inflating the reported sequence length.

This approach is brittle because:
1. It couples the conv layer's state detection to the attention layer's cache update ordering
2. The `past_seen_tokens` adjustment logic is error-prone and hard to reason about, especially with different `layer_types` configurations
3. The Mamba-family models in transformers (e.g., `Jamba`, `Zamba`) use an explicit state-tracking flag on the cache object instead, making the LFM2 approach inconsistent with the rest of the codebase

The conv cache also updates its state inline within each forward method rather than through a centralized method, leading to duplicated cache-update logic across `slow_forward` and `cuda_kernels_forward` (and across `lfm2`, `modular_lfm2`, and `lfm2_moe`).

## Affected Files

- `src/transformers/models/lfm2/modular_lfm2.py` — the source-of-truth modular file
- `src/transformers/models/lfm2/modeling_lfm2.py` — generated from modular
- `src/transformers/models/lfm2_moe/modeling_lfm2_moe.py` — MoE variant with same cache pattern

## Expected Behavior

The cache should track whether it has completed an initial prefill pass using an explicit boolean flag, consistent with other Mamba-style caches in the transformers library. Conv cache updates should go through a single centralized method to avoid logic duplication and keep the forward methods clean.

## Hints

- Look at how `JambaHybridDynamicCache` or `ZambaHybridDynamicCache` handle their `has_previous_state` tracking
- The `reset()` method on the cache should also clear any new state tracking
- Changes need to be consistent across all three files and both forward paths (`slow_forward` and `cuda_kernels_forward`)
