# [CI] Fix collect_tests failure for nightly-only GPU model tests

## Problem

`collect_tests()` in `python/sglang/test/ci/ci_register.py` raises `ValueError: No CI registry found` when processing certain test files in `test/registered/8-gpu-models/`. These files contain nightly-only CI registrations (using `nightly=True` for the `nightly-8-gpu-common` suite) that are intended for manual execution only, not for the standard CI test auto-discovery pipeline.

The problematic files are in `test/registered/8-gpu-models/` and can be identified by their `nightly=True` CI registration parameter. There are three such files for these models:
- Qwen3-235B
- DeepSeek-V3.1
- GLM-4.6-FP8

The repository already has a `test/manual/` directory used for tests that are not part of CI auto-discovery.

## Expected Outcome

After fixing, `collect_tests()` should complete without raising `ValueError` when scanning `test/registered/`. The nightly-only test files should be available under `test/manual/` for manual execution, properly adapted for standalone use without CI auto-discovery infrastructure. All remaining files in `test/registered/8-gpu-models/` should continue to have valid CI registrations. The test logic within the moved files (model paths, test functions, etc.) must be preserved unchanged.

## Notes

- Ensure any modified files are valid Python that passes syntax checks
