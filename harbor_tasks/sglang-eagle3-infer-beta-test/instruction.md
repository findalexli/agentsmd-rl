# Update EAGLE test configuration to EAGLE3

## Problem

The EAGLE speculative decoding tests use an older EAGLE configuration that does not match the current EAGLE3 implementation. The tests fail because the file references outdated constants, class names, algorithm settings, and threshold values.

## Expected Behavior

The test file must be updated so all tests pass. Specifically:

- The file must import EAGLE3 constants from the test utilities (`DEFAULT_DRAFT_MODEL_EAGLE3` and `DEFAULT_TARGET_MODEL_EAGLE3`)
- The file must define test classes named `TestEagle3ServerBase` and `TestEagle3ServerPage`
- The speculative algorithm setting must be set to `EAGLE3` (not `EAGLE`)
- The file must include EAGLE3-specific launch arguments: `--dtype=float16` and `--chunked-prefill-size` with value `1024`
- The file must handle the environment variable `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN`
- Test output statements must use the name `TestEagle3LargeBS`
- The GSM8K score threshold must be updated from `0.22` to `0.7`

All related EAGLE test files should continue to compile without errors.

## Constraints

- Do not introduce old EAGLE (non-EAGLE3) constants like `DEFAULT_DRAFT_MODEL_EAGLE` or `DEFAULT_TARGET_MODEL_EAGLE`
- Do not retain old class names like `TestEagleServerBase`, `TestEagleServerPage`, or `TestEagleLargeBS`
- Do not retain the old score threshold value `0.22`
- Do not use the old algorithm value `EAGLE`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `black (Python formatter)`
