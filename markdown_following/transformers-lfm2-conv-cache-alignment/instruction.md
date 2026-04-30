# LFM2 Hybrid Conv Cache: Incorrect Prefill/Decode State Detection

## Bug Description

The `Lfm2HybridConvCache` class in `src/transformers/models/lfm2/` (and correspondingly in `lfm2_moe`) has a fragile mechanism for deciding whether conv layers should run in "prefill" mode (first pass) vs "decode" mode (subsequent tokens).

Currently, the conv module's `slow_forward` and `cuda_kernels_forward` methods compute a `past_seen_tokens` value from the cache's `get_seq_length()` method, then apply a correction by subtracting `seqlen` if a `full_attention` layer appears before the current conv layer in the layer ordering. This correction is needed because the attention layer may have already appended to the KV cache, inflating the reported sequence length.

This approach is brittle because:
1. It couples the conv layer's state detection to the attention layer's cache update ordering
2. The `past_seen_tokens` adjustment logic is error-prone and hard to reason about, especially with different `layer_types` configurations
3. The Mamba-family models in transformers (e.g., `Jamba`, `Zamba`) use an explicit state-tracking flag named `has_previous_state` on the cache object instead, making the LFM2 approach inconsistent with the rest of the codebase

The conv cache also updates its state inline within each forward method rather than through a centralized method, leading to duplicated cache-update logic across `slow_forward` and `cuda_kernels_forward` (and across `lfm2`, `modular_lfm2`, and `lfm2_moe`).

## Affected Files

- `src/transformers/models/lfm2/modular_lfm2.py` — the source-of-truth modular file
- `src/transformers/models/lfm2/modeling_lfm2.py` — generated from modular
- `src/transformers/models/lfm2_moe/modeling_lfm2_moe.py` — MoE variant with same cache pattern

## Expected Behavior

The cache should track whether it has completed an initial prefill pass using an explicit boolean attribute named `has_previous_state`, consistent with other Mamba-style caches in the transformers library. The cache should also expose:

- An integer attribute `last_conv_layer` that identifies the index of the last convolutional layer in the model's `layer_types` configuration
- A method `update_conv_state(layer_idx, new_conv_state, cache_init=False)` that centralizes all conv cache updates. When `cache_init=True`, the method should store the full state tensor. When `cache_init=False`, the method should roll the cache left by one position and update the last position with the new values
- The `has_previous_state` flag should start as `False` and flip to `True` only when `update_conv_state` is called on the `last_conv_layer` index
- The `reset()` method should clear `has_previous_state` back to `False`

The forward methods (`slow_forward` and `cuda_kernels_forward`) should use `has_previous_state` to determine whether to run in prefill vs decode mode, rather than computing `past_seen_tokens` from the KV cache length.

## Hints

- Look at how `JambaHybridDynamicCache` or `ZambaHybridDynamicCache` handle their `has_previous_state` tracking
- The `reset()` method on the cache should also clear any new state tracking
- Changes need to be consistent across all three files and both forward paths (`slow_forward` and `cuda_kernels_forward`)
- The `last_conv_layer` can be computed as the last occurrence of "conv" in the `layer_types` list

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
