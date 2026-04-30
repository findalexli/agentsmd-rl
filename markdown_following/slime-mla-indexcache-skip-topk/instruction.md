# Bug: AttributeError on `skip_topk` when using MLA models without NSA

## Summary

The `docker/patch/latest/sglang.patch` file modifies `python/sglang/srt/models/deepseek_v2.py` in sglang to add support for topk index caching across layers. However, the `skip_topk` and `next_skip_topk` attributes on `DeepseekV2AttentionMLA` are only initialized inside the `if self.use_nsa:` branch of `__init__`, specifically nested within the `if is_nextn:` sub-block. When the forward path accesses these attributes on an MLA model that doesn't use NSA (Native Sparse Attention), it raises an `AttributeError`.

## Steps to Reproduce

1. Configure a DeepseekV2-style MLA model **without** NSA enabled
2. Apply the sglang patch
3. Run inference — the model crashes in `forward_absorb_prepare` because `self.skip_topk` and `self.next_skip_topk` were never set

## Relevant Code

- File: `docker/patch/latest/sglang.patch`
- The patch modifies `DeepseekV2AttentionMLA.__init__` in `python/sglang/srt/models/deepseek_v2.py`
- The `forward_absorb_prepare` method references `self.skip_topk` and `self.next_skip_topk` unconditionally when determining the return value

## Expected Behavior

`self.skip_topk` and `self.next_skip_topk` must be initialized unconditionally at method-body level in `__init__` (i.e., at the top-level indentation of the method body, outside the `if self.use_nsa:` conditional block entirely), defaulting to `False`, so that MLA models without NSA can proceed through the forward path without errors.

Specifically:

- **Unconditional init**: `self.skip_topk` and `self.next_skip_topk` should be assigned `False` at method-body level of `__init__` — they must not be nested inside `if self.use_nsa:` or `if is_nextn:` conditionals.
- **`forward_absorb_prepare` return value**: This method must return a 2-tuple `(output, topk_indices)`. When `self.skip_topk` is `True`, it should `return output, None`. When not skipping, it should `return output, <topk_indices_value>` (i.e., the return line should start with `return output,` and include the topk indices). The method must also reference `self.next_skip_topk` in its return path logic.
- **NSA config attributes preserved**: The NSA branch must still configure `index_topk_freq`, `index_topk_pattern`, and `index_skip_topk_offset`.
- **Forward skip logic**: The forward path must conditionally skip the indexer based on `self.skip_topk`, using `prev_topk_indices` as a fallback. There should be conditional logic such as `if not self.skip_topk` or `if self.skip_topk` that governs whether to run the indexer or use `prev_topk_indices`.

## Additional Context

The `DeepseekV2DecoderLayer.forward` method and `DeepseekV2Model` also need updates to thread topk indices across layers:

- **DecoderLayer return**: `DeepseekV2DecoderLayer.forward` must return a 3-tuple containing `hidden_states`, `residual`, and the topk indices (e.g., `return hidden_states, residual, topk_indices`).
- **Model unpacking**: In the `DeepseekV2Model` forward loop, the 3-tuple from each layer must be unpacked into variables including `hidden_states`, `residual`, and the topk indices (the unpacking assignment should name all three).
- All of these changes are within the sglang.patch file.

The topk index caching logic (frequency-based or pattern-based skipping) should remain functional for NSA-enabled models.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check` (including import sorting via isort)
