# Bug: VLM dtype validation blocks SFT training unnecessarily

## Summary

When using Vision-Language Models (VLMs) like `Qwen/Qwen3-VL-4B-Instruct` with supervised fine-tuning (SFT), creating a valid `SFTConfig` fails with a `ValueError` even though the dtype constraint is only relevant for RL training.

## Details

When instantiating a config with a VLM model name and default dtypes (float32), the system raises:

```python
ValueError: VLM models must use optimization_dtype='bfloat16' and reduce_dtype='bfloat16' ...
```

This blocks SFT workflows that use VLMs with default settings.

## Expected behavior

The dtype validation for VLMs should only apply to RL training contexts, not SFT. Specifically:
- RL training configs (`TrainerConfig`) must reject VLM models with non-bfloat16 dtypes, raising `ValueError` with "bfloat16" in the error message. This applies to VLM model names including `Qwen/Qwen3-VL-4B-Instruct`, `Qwen/Qwen3-VL-72B`, and `Qwen/Qwen3.5-VL-7B`.
- `SFTConfig` with VLM models and default float32 dtypes should succeed without errors
- `ModelConfig` with VLM names and default dtypes should succeed without errors

## Reproduction

```python
from prime_rl.configs.sft import SFTConfig
from prime_rl.configs.trainer import ModelConfig

# This currently raises ValueError but should work
mc = ModelConfig(name="Qwen/Qwen3-VL-4B-Instruct")
sc = SFTConfig(model=mc)  # Should not raise
```

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
