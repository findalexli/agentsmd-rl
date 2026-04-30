# Task: sglang-reasoning-tokens-test-kit

## Problem

The reasoning token usage tests currently run from a standalone test file (`test_reasoning_usage_tokens.py`) that launches **3 dedicated servers** (non-spec DeepSeek-R1, spec/EAGLE3, spec-v2/EAGLE3) only for these tests. This wastes GPU resources and CI time — the same server configurations already exist in other test classes (`TestEnableThinking`, `TestQwen35FP4MTP`, and `TestQwen35FP4MTPV2`) that run with `--reasoning-parser qwen3`.

## Goal

Consolidate the reasoning token tests so they reuse existing server fixtures instead of launching new ones. The net effect should be **3 fewer server launches**, with zero additional GPU time.

## What the final state should look like

After consolidation:

- There is a reusable test kit (a Python mixin class) named `ReasoningTokenUsageMixin` that provides these reasoning token usage test methods: `test_reasoning_tokens_thinking`, `test_reasoning_tokens_non_thinking`, `test_reasoning_tokens_thinking_stream`, `test_reasoning_tokens_non_thinking_stream`, and `test_reasoning_tokens_generate_exact_count`
- The mixin includes a classmethod named `init_reasoning_token_verifier` that consuming test classes must call from their `setUpClass` method as `cls.init_reasoning_token_verifier()`
- The mixin relies on class attributes `model`, `base_url`, and `reasoning_parser_name` that consuming test classes must define
- The standalone reasoning token test file `test_reasoning_usage_tokens.py` has been removed
- The mixin is integrated into the existing test classes `TestEnableThinking`, `TestQwen35FP4MTP`, and `TestQwen35FP4MTPV2` — these classes already launch servers with `--reasoning-parser qwen3`
- Each consuming test class sets `reasoning_parser_name = "qwen3"` as a class attribute
- `TestQwen35FP4` inherits from `CustomTestCase` instead of `unittest.TestCase`
- All pre-commit hooks pass (ruff, isort, codespell, black-jupyter, check-ast, check-yaml, check-toml, check-workflow-job-names, sort-ci-permissions, check-symlinks, destroyed-symlinks, trailing-whitespace, end-of-file-fixer, check-added-large-files, check-merge-conflict, check-shebang-scripts-are-executable, detect-private-key, and debug-statements)
