# CI Test Failures: Phi-3 and SDPA Flash Dispatch

## Problem

Recent CI runs on `main` are failing in two areas:

### 1. Phi-3 Integration Tests

Four integration tests in `tests/models/phi3/test_modeling_phi3.py` are failing with errors when calling model generation methods:
- `test_phi3_mini_4k_instruct_generation`
- `test_phi3_mini_4k_instruct_with_static_cache`
- `test_phi3_mini_128k_instruct_generation`
- `test_phi3_mini_128k_instruct_with_static_cache`

The test logs show these tests produce errors related to argument handling when calling `model.generate()` or the static-cache generate helper.

### 2. SDPA Flash Attention Dispatch Test

`test_sdpa_can_dispatch_on_flash` in `tests/test_modeling_common.py` is failing for these model families:
- **Pi0** (pi0)
- **Parakeet** encoder (parakeet_encoder)
- **Parakeet** CTC (parakeet_ctc)
- **Evolla** (EvollaModel)

The CI logs indicate these models fail during the SDPA flash attention dispatch test, similar to how PaliGemma and other models currently skip this test.

## Files to Investigate

- `tests/models/phi3/test_modeling_phi3.py`
- `tests/test_modeling_common.py`

## Expected Behavior After Fix

- All four Phi-3 test methods should pass without producing argument-related errors
- The SDPA test should handle the Pi0, Parakeet encoder/CTC, and Evolla model families appropriately
- Existing skip entries for modernbert, gemma3, pixtral, sam, kosmos-2, and mllama must be preserved

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
