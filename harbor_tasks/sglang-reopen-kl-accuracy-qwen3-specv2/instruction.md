# Re-enable KL Divergence Test for Qwen3 + SpecV2

The test file `test/registered/4-gpu-models/test_qwen3_next_models_mtp.py` contains test classes for Qwen3-Next models with speculative decoding. The `TestQwen3NextMTPV2` class is currently missing KL divergence accuracy testing that other similar test classes have.

## The Problem

When examining the test file, you'll notice that:

1. `TestQwen3NextMTP` includes `KLDivergenceMixin` and has `kl_div_thres = 0.0025`
2. `TestQwen3NextMTPTopk` includes `KLDivergenceMixin` and has `kl_div_thres = 0.008`
3. `TestQwen3NextMTPV2` only inherits from `GSM8KMixin` and `DefaultServerBase` — it's missing `KLDivergenceMixin`

There's also a TODO comment in the file explaining that `KLDivergenceMixin` should be added back after a fix for SpecV2 log probability handling was merged.

## What Needs to Be Done

Update the `TestQwen3NextMTPV2` class to:

1. Add `KLDivergenceMixin` to its inheritance (alongside `GSM8KMixin` and `DefaultServerBase`)
2. Add `kl_div_thres = 0.0025` class attribute
3. Remove the TODO comment about re-adding `KLDivergenceMixin`

## Location

- File: `test/registered/4-gpu-models/test_qwen3_next_models_mtp.py`
- Look for the `TestQwen3NextMTPV2` class definition

## Notes

- The file uses imports from `sglang.test.kits.eval_accuracy_kit`, `sglang.test.kits.kl_divergence_kit`, etc.
- The test class runs with `SGLANG_ENABLE_SPEC_V2` environment variable set to `True`
- Make sure not to break existing class attributes like `gsm8k_accuracy_thres = 0.93`
