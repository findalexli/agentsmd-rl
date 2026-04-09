# Switch eagle_infer_beta to EAGLE3

## Problem

The test file `test/registered/spec/eagle/test_eagle_infer_beta.py` is using outdated EAGLE speculative decoding configuration constants and settings. It needs to be updated to use the new EAGLE3 speculative decoding algorithm.

The file currently:
- Imports `DEFAULT_DRAFT_MODEL_EAGLE` and `DEFAULT_TARGET_MODEL_EAGLE` constants
- Uses class names `TestEagleServerBase` and `TestEagleServerPage`
- Sets `--speculative-algorithm EAGLE`
- Uses a low score threshold of 0.22 for GSM8K tests

## Expected Behavior

The test file should be updated to:
- Import `DEFAULT_DRAFT_MODEL_EAGLE3` and `DEFAULT_TARGET_MODEL_EAGLE3` constants
- Rename classes to `TestEagle3ServerBase` and `TestEagle3ServerPage`
- Set `--speculative-algorithm EAGLE3`
- Add `--dtype=float16` and `--chunked-prefill-size 1024` launch arguments
- Add `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN` environment override
- Update test print statement to use `TestEagle3LargeBS`
- Update GSM8K score threshold from 0.22 to 0.7

## Files to Look At

- `test/registered/spec/eagle/test_eagle_infer_beta.py` — The test file requiring updates
