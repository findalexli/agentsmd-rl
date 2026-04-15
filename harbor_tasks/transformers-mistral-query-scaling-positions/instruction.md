# Bug: Incorrect query scaling in attention layers

## Summary

Attention layers in certain Mistral-family models apply a position-dependent scaling factor to query states. The current implementation uses absolute sequence positions derived from cache length rather than the actual per-token positions provided by the caller. Additionally, the scaling factor's shape does not broadcast correctly against the 4D query tensor.

## Expected behavior

The `get_llama_4_attn_scale` function must:

1. Accept a **2D tensor** of shape `(batch_size, seq_len)` representing the actual position of each token in the batch (accounting for padding, packing, etc.)
2. Compute scaling using the formula: `1 + beta * log(1 + floor(position / max_position))`
3. Return a **4D tensor** of shape `(batch_size, 1, seq_len, 1)` that broadcasts correctly with query states of shape `(batch, heads, seq, head_dim)`

When different batch items have different position sequences, their scaling factors must differ accordingly.

The `forward()` method of the attention classes must accept an explicit `position_ids` parameter and pass it to the scaling function instead of computing absolute positions internally.

## Affected models

The same scaling logic appears in multiple model files under `src/transformers/models/` for Mistral4 and Ministral3 architectures. All must be corrected consistently.
