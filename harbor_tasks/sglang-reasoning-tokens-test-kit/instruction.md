# Task: sglang-reasoning-tokens-test-kit

## Problem

The reasoning token usage tests currently run from a standalone test file that launches **3 dedicated servers** (non-spec DeepSeek-R1, spec/EAGLE3, spec-v2/EAGLE3) only for these tests. This wastes GPU resources and CI time — the same server configurations already exist in other test classes that run with `--reasoning-parser qwen3`.

## Goal

Consolidate the reasoning token tests so they reuse existing server fixtures instead of launching new ones. The net effect should be **3 fewer server launches**, with zero additional GPU time.

## What the final state should look like

After consolidation:

- There is a reusable test kit (a Python mixin class) that provides reasoning token usage test methods
- The standalone reasoning token test file has been removed
- The test kit is integrated into the existing test classes that already launch servers with `--reasoning-parser qwen3`
- All pre-commit hooks pass

## Validation

Your changes must pass all pre-commit hooks (ruff, isort, codespell, black-jupyter, check-ast, check-yaml, check-toml, etc.) and the Python files must parse as valid AST.