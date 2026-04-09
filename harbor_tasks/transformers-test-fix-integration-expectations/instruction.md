# Fix failing T5ModelIntegrationTest and Qwen2IntegrationTest

## Problem

Two integration tests are currently failing in the transformers repository:

1. **Qwen2 test_speculative_generation**: The test uses inconsistent model references - it loads the tokenizer from "Qwen/Qwen2-7B" but the model from "Qwen/Qwen2-0.5B". This mismatch can cause issues with vocabulary alignment. Additionally, the test uses a plain string for `EXPECTED_TEXT_COMPLETION`, but model outputs vary by platform (CUDA version, etc.). Other tests in the same file use the `Expectations` class to handle platform-specific expected values.

2. **T5 test_compile_static_cache**: The test uses `tokenizer.batch_decode()` for single-item outputs, but `batch_decode()` is designed for batch outputs. For single tensor outputs from `generate()`, `tokenizer.decode()` should be used instead.

## Files to Look At

- `tests/models/qwen2/test_modeling_qwen2.py` — Look at `test_speculative_generation` method around line 185
- `tests/models/t5/test_modeling_t5.py` — Look at `test_compile_static_cache` method around line 1428

## What Needs to Change

For the Qwen2 test:
- Change the tokenizer model from "Qwen/Qwen2-7B" to "Qwen/Qwen2-0.5B" for consistency
- Wrap the expected output in an `Expectations` object with platform-specific values (similar to other tests in the file like `test_model_450m_logits`)

For the T5 test:
- Change all three instances of `tokenizer.batch_decode(generated_ids, ...)` to `tokenizer.decode(generated_ids, ...)` in the `test_compile_static_cache` method

These are test fixes - the underlying library code is correct, but the tests themselves have bugs that need correction.
