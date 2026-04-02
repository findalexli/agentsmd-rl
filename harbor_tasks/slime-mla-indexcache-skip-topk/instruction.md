# Bug: AttributeError on `skip_topk` when using MLA models without NSA

## Summary

The `docker/patch/latest/sglang.patch` file modifies `python/sglang/srt/models/deepseek_v2.py` in sglang to add support for topk index caching across layers. However, the `skip_topk` and `next_skip_topk` attributes on `DeepseekV2AttentionMLA` are only initialized inside the `if self.use_nsa:` branch of `__init__`. When the forward path accesses these attributes on an MLA model that doesn't use NSA (Native Sparse Attention), it raises an `AttributeError`.

## Steps to Reproduce

1. Configure a DeepseekV2-style MLA model **without** NSA enabled
2. Apply the sglang patch
3. Run inference — the model crashes in `forward_absorb_prepare` because `self.skip_topk` and `self.next_skip_topk` were never set

## Relevant Code

- File: `docker/patch/latest/sglang.patch`
- The patch modifies `DeepseekV2AttentionMLA.__init__` in `python/sglang/srt/models/deepseek_v2.py`
- The `skip_topk` / `next_skip_topk` attributes are initialized at around line `@@ -1174` of the patch, only inside the `if self.use_nsa:` block
- The `forward_absorb_prepare` method references `self.skip_topk` and `self.next_skip_topk` unconditionally at the end when determining the return value

## Expected Behavior

`skip_topk` and `next_skip_topk` should always be available on the attention module, defaulting to safe values (`False`) so that MLA models without NSA can still proceed through the forward path without errors. The topk index caching logic (frequency-based or pattern-based skipping) should remain functional for NSA-enabled models.

## Additional Context

The `DeepseekV2DecoderLayer.forward` method also needs to properly thread the `prev_topk_indices` through the attention call and unpack the return tuple, and `DeepseekV2Model` needs to pass `topk_indices` across layers. All of these changes are within the sglang.patch file.
