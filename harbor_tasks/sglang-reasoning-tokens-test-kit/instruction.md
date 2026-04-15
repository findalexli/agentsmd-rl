# Consolidate reasoning token tests to reuse existing server fixtures

## Problem

The reasoning token usage tests currently run from a standalone file that launches **3 dedicated servers** (non-spec DeepSeek-R1, spec/EAGLE3, spec-v2/EAGLE3) only for these tests. This wastes GPU resources and CI time — the same server configurations already exist in other test classes that run with `--reasoning-parser qwen3`.

## Goal

Consolidate the reasoning token tests so they reuse existing server fixtures instead of launching new ones. The net effect should be **3 fewer server launches**, with zero additional GPU time.

## What to do

1. Remove the standalone reasoning token test file (`test/registered/openai_server/features/test_reasoning_usage_tokens.py`)

2. Extract the test logic into a reusable test kit in `python/sglang/test/kits/` (create the directory if it doesn't exist)

3. Integrate the test kit into the test classes that already launch servers with `--reasoning-parser qwen3`:
   - `test_enable_thinking.py::TestEnableThinking`
   - `test_qwen35_models.py::TestQwen35FP4MTP`
   - `test_qwen35_models.py::TestQwen35FP4MTPV2`

4. Also fix `TestQwen35FP4` in `test_qwen35_models.py` to use `CustomTestCase` instead of `unittest.TestCase` (it already inherits from `CustomTestCase` in the other two classes)

## Expected file structure

- `python/sglang/test/kits/reasoning_tokens_kit.py` — new shared test kit
- `test/registered/openai_server/features/test_reasoning_usage_tokens.py` — deleted

The kit should provide test methods that verify:
- Reasoning tokens are counted correctly in chat completions with and without thinking enabled
- Reasoning tokens are counted correctly in streaming chat completions
- The `/generate` API correctly reports reasoning token counts

Each test class that uses the kit must set `reasoning_parser_name = "qwen3"` and call the kit's initializer in `setUpClass`.

## Validation

Your changes must pass all pre-commit hooks (ruff, isort, codespell, black-jupyter, check-ast, check-yaml, check-toml, etc.) and the Python files must parse as valid AST.