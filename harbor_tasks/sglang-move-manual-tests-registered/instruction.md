# [CI] Move manual-only nightly tests out of test/registered/

## Problem

Three test files in `test/registered/8-gpu-models/` are causing `collect_tests()` to fail with `ValueError: No CI registry found`. These are manual-only nightly tests that were incorrectly placed in the auto-discovered `test/registered/` directory.

The failing files are:
- `test/registered/8-gpu-models/test_qwen3_235b.py`
- `test/registered/8-gpu-models/test_deepseek_v31.py`
- `test/registered/8-gpu-models/test_glm_46_fp8.py`

These files contain `register_cuda_ci()` calls with `nightly=True` for the `nightly-8-gpu-common` suite, but they should not be auto-discovered by the CI test runner since they are intended for manual execution only.

## Expected Behavior

1. Move the three test files from `test/registered/8-gpu-models/` to `test/manual/`
2. Remove the `register_cuda_ci()` calls from these files
3. Remove the `from sglang.test.ci.ci_register import register_cuda_ci` imports

This will prevent `collect_tests()` from discovering these manual tests while keeping them available for manual execution when needed.

## Files to Look At

- `test/registered/8-gpu-models/test_qwen3_235b.py` — Qwen3-235B test with CI registration
- `test/registered/8-gpu-models/test_deepseek_v31.py` — DeepSeek-V3.1 test with CI registration
- `test/registered/8-gpu-models/test_glm_46_fp8.py` — GLM-4.6-FP8 test with CI registration
- `python/sglang/test/ci/ci_register.py` — Contains `collect_tests()` function (for reference)

## Notes

- The `test/manual/` directory already exists and is used for non-CI tests
- The files should be moved (preserving git history via `git mv` if possible)
- The test logic itself should remain unchanged; only the CI registration should be removed
