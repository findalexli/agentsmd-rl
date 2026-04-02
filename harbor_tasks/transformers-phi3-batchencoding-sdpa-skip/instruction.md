# CI Test Failures: Phi-3 and SDPA Flash Dispatch

## Problem

Recent CI runs on `main` are failing in two areas:

### 1. Phi-3 Integration Tests

Several Phi-3 integration tests in `tests/models/phi3/test_modeling_phi3.py` are failing with errors about unexpected argument types when calling `model.generate()` or the static-cache generate helper.

The root cause is that `apply_chat_template(..., return_tensors="pt")` now returns a `BatchEncoding` object (a dict-like mapping with keys like `"input_ids"` and `"attention_mask"`) rather than a raw tensor. The test code passes this object directly where a tensor or keyword arguments are expected.

Affected test methods:
- `test_phi3_mini_4k_instruct_generation` — calls `model.generate(inputs, ...)`
- `test_phi3_mini_4k_instruct_with_static_cache` — passes dict to `Phi3MiniWithStaticCache.generate(model, inputs, 64)` which expects a tensor
- `test_phi3_mini_128k_instruct_generation` — same pattern as the 4k variant
- `test_phi3_mini_128k_instruct_with_static_cache` — same pattern as the 4k static cache variant

### 2. SDPA Flash Attention Dispatch Test

`test_sdpa_can_dispatch_on_flash` in `tests/test_modeling_common.py` forces only the Flash SDPA kernel, which rejects any non-null attention mask. Some models generate or inject an attention mask internally even when `attention_mask=None` is passed by the test:

- **Pi0** wraps PaliGemma, which creates a causal mask mapping internally (PaliGemma itself is already skipped for this reason)
- **Parakeet** (both encoder and CTC variants) always passes a relative-position bias as the attention mask
- **Evolla** has a protein encoder that generates an attention mask internally when none is provided

These three model families need to be handled the same way PaliGemma and other already-skipped models are handled in `test_sdpa_can_dispatch_on_flash`.

## Files to Investigate

- `tests/models/phi3/test_modeling_phi3.py`
- `tests/test_modeling_common.py` (look at `test_sdpa_can_dispatch_on_flash` and its existing skip list)
