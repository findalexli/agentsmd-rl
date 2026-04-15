# Update EAGLE test configuration to EAGLE3

## Problem

The EAGLE speculative decoding tests in `test/registered/spec/eagle/test_eagle_infer_beta.py` use an older EAGLE configuration that does not match the current EAGLE3 implementation. The tests fail because the file references outdated constants, class names, algorithm settings, and threshold values.

## Expected Behavior

The test file must be updated so all tests pass. Specifically:

- The file must import EAGLE3 constants from the test utilities (such as `DEFAULT_DRAFT_MODEL_EAGLE3` and `DEFAULT_TARGET_MODEL_EAGLE3`)
- The file must use EAGLE3 class names (test classes follow a naming convention with `Eagle3` in the name)
- The speculative algorithm setting must be set to `EAGLE3`
- The file must include EAGLE3-specific launch arguments: `--dtype` with value `float16` and `--chunked-prefill-size` with value `1024`
- The file must add an environment override using the `override()` pattern for `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN`
- Test output statements must use EAGLE3 naming
- The GSM8K score threshold must be updated to a value appropriate for EAGLE3

The file `test/registered/spec/eagle/test_eagle_infer_beta.py` should compile without errors and all related EAGLE test files in `test/registered/spec/eagle/` should continue to compile.

## Constraints

- Do not introduce new EAGLE (non-EAGLE3) constants or class names
- Do not retain the old score threshold value
- Do not use old class names like `TestEagleLargeBS`