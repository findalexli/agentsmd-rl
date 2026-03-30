# MoE token dispatcher type not propagated in bridge model provider

## Problem

In `slime/backends/megatron_utils/model_provider.py`, when using bridge mode (`args.megatron_to_hf_mode == "bridge"`), several configuration attributes from `args` are manually propagated to the bridge provider object. However, `moe_token_dispatcher_type` is not propagated.

Slime always sets `variable_seq_lengths=True`, but the default `moe_token_dispatcher_type` is `"allgather"`, which does not support variable sequence lengths. When `provider.finalize()` is called, it raises:

```
ValueError: Token dispatcher type: allgather does not support variable sequence length
```

The `moe_token_dispatcher_type` attribute on `args` needs to be propagated to the provider, just like `sequence_parallel`, `context_parallel_size`, `variable_seq_lengths`, and other attributes already are.

## Expected Behavior

The bridge model provider should receive the `moe_token_dispatcher_type` from args (when the attribute exists), so that `finalize()` uses a dispatcher compatible with variable sequence lengths.

## File to Modify

- `slime/backends/megatron_utils/model_provider.py` -- the `wrapped_model_provider()` function, in the bridge mode block
