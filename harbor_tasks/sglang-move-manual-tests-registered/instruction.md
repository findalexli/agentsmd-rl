# [CI] Fix collect_tests failure for nightly-only GPU model tests

## Problem

`collect_tests()` in `python/sglang/test/ci/ci_register.py` raises `ValueError: No CI registry found` when processing certain test files in `test/registered/8-gpu-models/`. These files use `register_cuda_ci()` with `nightly=True` for the `nightly-8-gpu-common` suite, meaning they are intended for manual execution only, not for the standard CI test auto-discovery pipeline.

The three problematic files are:
- `test_qwen3_235b.py`
- `test_deepseek_v31.py`
- `test_glm_46_fp8.py`

Each of these files currently imports from `sglang.test.ci.ci_register` and calls `register_cuda_ci()` at module level. The repository already has a `test/manual/` directory used for tests that are not part of CI auto-discovery.

## Expected Outcome

1. The three files listed above should no longer exist in `test/registered/8-gpu-models/` and should instead be available under `test/manual/`.
2. Since files in `test/manual/` are run standalone (outside the CI auto-discovery pipeline), the `register_cuda_ci()` calls and the `ci_register` imports are no longer appropriate and should not be present in the moved files.
3. `collect_tests()` should complete without raising `ValueError` when scanning `test/registered/`.
4. All remaining files in `test/registered/8-gpu-models/` should continue to have valid CI registrations.
5. The test logic within the moved files (model paths, test functions, etc.) must be preserved unchanged.

## Notes

- Ensure any modified files are valid Python that passes syntax checks, linting (ruff, black, isort, codespell), and pre-commit hooks.
