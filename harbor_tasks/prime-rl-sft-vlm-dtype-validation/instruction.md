# Bug: VLM dtype validation blocks SFT training unnecessarily

## Summary

When configuring supervised fine-tuning (SFT) for a Vision-Language Model (VLM) such as `Qwen/Qwen3-VL-4B-Instruct`, creating a valid `SFTConfig` fails with a `ValueError` even though the dtype constraint only makes sense for RL training.

## Details

The `ModelConfig` class in `src/prime_rl/configs/trainer.py` has a pydantic `model_validator` that enforces `optimization_dtype='bfloat16'` and `reduce_dtype='bfloat16'` for any VLM model name. This was added to match vLLM inference dtypes during RL training.

However, `ModelConfig` is shared between the RL trainer (`TrainerConfig`) and the SFT trainer (`SFTConfig` in `src/prime_rl/configs/sft.py`). SFT does not use vLLM inference, so there is no reason to require bfloat16 dtypes. The default dtypes are `float32`, which means any SFT config with a VLM model name is rejected unless the user manually overrides both dtype fields — a confusing and unnecessary constraint.

## Reproduction

Instantiating a `ModelConfig` with a VLM name and default dtypes raises:

```python
from prime_rl.configs.trainer import ModelConfig
ModelConfig(name="Qwen/Qwen3-VL-4B-Instruct")
# ValueError: VLM models must use optimization_dtype='bfloat16' and reduce_dtype='bfloat16' ...
```

This blocks SFT workflows that use VLMs with default settings.

## Expected behavior

The bfloat16 dtype constraint for VLMs should only apply in the RL training context, not for SFT. SFT users should be able to use VLM models with any valid dtype configuration.

## Relevant files

- `src/prime_rl/configs/trainer.py` — `ModelConfig` and `TrainerConfig` classes
- `src/prime_rl/configs/sft.py` — `SFTConfig` class (uses `ModelConfig`)
- `src/prime_rl/utils/vlm.py` — `is_vlm_model()` helper
