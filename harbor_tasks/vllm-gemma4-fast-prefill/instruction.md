# Enable Fast Prefill Optimization for Gemma 4

## Problem

The Gemma 4 model implementation in vLLM does not support the `--kv-sharing-fast-prefill` flag. Gemma 4 uses KV-sharing (cross-attention layers that share KV caches with earlier self-attention layers), but when `kv_sharing_fast_prefill` is enabled, there is no YOCO (You Only Cache Once) optimization — cross-decoder layers still process all prefill tokens even though they share cached KV values, wasting compute during prefill.

The Gemma 3n model already has this optimization implemented. The Gemma 4 model needs the same pattern: split decoder layers into two groups (self-decoder layers that run on all tokens, and cross-decoder layers that skip prefill tokens and only process decode tokens), with appropriate `torch.compile` support for each group.

## Expected Behavior

When `kv_sharing_fast_prefill` is enabled in the cache config:

1. The model should split its decoder layers into a **self-decoder** group (non-KV-shared layers) and a **cross-decoder** group (KV-shared layers)
2. During forward pass, the self-decoder processes all tokens normally
3. The cross-decoder only processes decode tokens (skipping prefill tokens), using `KVSharingFastPrefillMetadata` to determine which tokens to pass through
4. Each layer group should be independently compilable via `@support_torch_compile` with appropriate `enable_if` conditions
5. The normal (non-fast-prefill) forward path must continue working unchanged

## Files to Look At

- `vllm/model_executor/models/gemma4.py` — The Gemma 4 model implementation. Currently has a single `Gemma4Model` class that processes all layers inline. Needs the YOCO split.
- `vllm/model_executor/models/gemma3n.py` — Reference: the Gemma 3n model already implements this pattern with `Gemma3nSelfDecoderLayers` and `Gemma3nCrossDecoderLayers`
- `vllm/v1/attention/backends/utils.py` — Contains `KVSharingFastPrefillMetadata` used to identify decode-only tokens
- `vllm/forward_context.py` — Provides `get_forward_context()` for accessing attention metadata during forward pass
