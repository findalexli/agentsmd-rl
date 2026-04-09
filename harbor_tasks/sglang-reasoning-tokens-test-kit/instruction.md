# Refactor reasoning_tokens tests to use existing server fixtures

## Problem

The current test setup for reasoning token usage is inefficient. The standalone `test_reasoning_usage_tokens.py` file launches **3 dedicated servers** (non-spec DeepSeek-R1, spec/EAGLE3, spec-v2/EAGLE3) only for reasoning_tokens tests. This wastes GPU resources and CI time.

## Expected Behavior

Refactor the reasoning token tests to:

1. **Remove the standalone test file** at `test/registered/openai_server/features/test_reasoning_usage_tokens.py`

2. **Create a reusable test kit** at `python/sglang/test/kits/reasoning_tokens_kit.py` containing:
   - A `ReasoningTokenUsageMixin` class with 5 test methods:
     - `test_reasoning_tokens_thinking` — non-streaming chat with thinking enabled
     - `test_reasoning_tokens_non_thinking` — non-streaming chat without thinking
     - `test_reasoning_tokens_thinking_stream` — streaming chat with thinking
     - `test_reasoning_tokens_non_thinking_stream` — streaming chat without thinking
     - `test_reasoning_tokens_generate_exact_count` — verify exact token count in /generate API
   - An `init_reasoning_token_verifier()` classmethod that initializes the tokenizer and token IDs

3. **Integrate the mixin into existing test classes** that already launch servers with `--reasoning-parser qwen3`:
   - `test_enable_thinking.py::TestEnableThinking` — non-spec, Qwen3-30B-A3B (1-GPU)
   - `test_qwen35_models.py::TestQwen35FP4MTP` — spec/NEXTN, Qwen3.5-397B (4-GPU)
   - `test_qwen35_models.py::TestQwen35FP4MTPV2` — spec-v2/NEXTN, same model (4-GPU)

4. **Fix TestQwen35FP4** to use `CustomTestCase` instead of `unittest.TestCase`

## Files to Look At

- `test/registered/openai_server/features/test_reasoning_usage_tokens.py` — the file to remove
- `test/registered/openai_server/features/test_enable_thinking.py` — add mixin to TestEnableThinking
- `test/registered/4-gpu-models/test_qwen35_models.py` — add mixin to TestQwen35FP4MTP and TestQwen35FP4MTPV2, fix TestQwen35FP4
- `python/sglang/test/kits/` — directory for the new test kit (may not exist yet)

## Hints

- The mixin needs attributes set on the test class: `model`, `base_url`, `reasoning_parser_name`
- Each test class using the mixin must call `cls.init_reasoning_token_verifier()` in `setUpClass`
- The mixin uses `requests` for HTTP calls to the running server
- Consider how `think_end_token_id` is computed from the tokenizer and reasoning parser

Net effect should be **3 fewer server launches**, with zero additional GPU time.
