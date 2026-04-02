# Bug: Incorrect query scaling in Mistral4 and Ministral3 attention

## Summary

The query scaling logic in `Mistral4Attention` and `Ministral3Attention` computes position-dependent scaling factors using **absolute sequence positions** derived from the cache length. This is incorrect for padded or packed sequences (e.g., continuous batching), where the actual position of each token may differ from its index in the sequence dimension.

## Affected files

- `src/transformers/models/ministral3/modeling_ministral3.py` — `get_llama_4_attn_scale()` and `Ministral3Attention.forward()`
- `src/transformers/models/ministral3/modular_ministral3.py` — same functions (modular source)
- `src/transformers/models/mistral4/modeling_mistral4.py` — `get_llama_4_attn_scale()` and `Mistral4Attention.forward()`
- `src/transformers/models/mistral4/modular_mistral4.py` — same functions (modular source)

## Details

The `get_llama_4_attn_scale` function computes a position-dependent scaling factor for queries. Currently, the attention `forward()` method constructs a 1D range of absolute positions from `past_seen_tokens`, which does not reflect the true positions of tokens in padded or packed batches. The caller already has access to the correct per-token positions, but this information is not being passed through.

Additionally, the tensor reshaping in `get_llama_4_attn_scale` does not properly account for the batch dimension, which means the scaling factor cannot broadcast correctly against the 4D query tensor `(batch, heads, seq, head_dim)`.

## Expected behavior

The scaling function should use the actual per-token position information (which accounts for padding, packing, etc.) and produce a tensor shape that broadcasts correctly with the 4D query states.
