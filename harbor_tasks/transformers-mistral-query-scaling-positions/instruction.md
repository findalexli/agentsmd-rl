# Bug: Incorrect query scaling in attention layers

## Summary

Attention layers in certain Mistral-family models apply a position-dependent scaling factor to query states. The current implementation uses absolute sequence positions derived from cache length rather than the actual per-token positions provided by the caller. Additionally, the scaling factor's shape does not broadcast correctly against the 4D query tensor.

## Expected behavior

The `get_llama_4_attn_scale` function must:

1. Accept a **2D tensor** of shape `(batch_size, seq_len)` representing the actual position of each token in the batch (accounting for padding, packing, etc.)
2. Compute scaling using the formula: `1 + beta * log(1 + floor(position / max_position))`
3. Return a **4D tensor** of shape `(batch_size, 1, seq_len, 1)` that broadcasts correctly with query states of shape `(batch, heads, seq, head_dim)`

When different batch items have different position sequences, their scaling factors must differ accordingly.

The `forward()` method of the attention classes (`Ministral3Attention` and `Mistral4Attention`) must accept an explicit `position_ids` parameter and pass it to the scaling function instead of computing absolute positions internally. The `forward()` method must not use an `absolute_positions` variable derived from cache state.

## Affected files

All four of the following files contain the bug and must be corrected consistently:

- `src/transformers/models/ministral3/modeling_ministral3.py`
- `src/transformers/models/ministral3/modular_ministral3.py`
- `src/transformers/models/mistral4/modeling_mistral4.py`
- `src/transformers/models/mistral4/modular_mistral4.py`

Note: `modular_mistral4.py` imports `get_llama_4_attn_scale` from `ministral3.modeling_ministral3` rather than defining its own copy, so the scaling function fix only needs to be applied where it is defined. However, the `forward()` method in all four files must be updated.

The repo CI checks (modeling structure, doctest list, dummies, ruff lint and format) must continue to pass on these files after the fix.
