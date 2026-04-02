# Bug: Text-only training fails for Qwen3.5 MoE models

## Problem

When loading a Qwen3.5 MoE model (e.g. `Qwen/Qwen3.5-35B-A3B`) for **text-only** training (no `[model.vlm]` section in the TOML config), the model loading fails with a `ValueError` from `AutoModelForCausalLMPrimeRL`.

The root cause is in `src/prime_rl/trainer/model.py` in the `get_model()` function. The code uses a single boolean flag to control both:

1. **Model class selection** — whether to use `AutoModelForImageTextToText` (which handles composite VLM configs natively) vs `AutoModelForCausalLM`/`AutoModelForCausalLMPrimeRL`
2. **Training behavior** — whether to freeze the vision encoder, apply FSDP sharding to the vision encoder, etc.

The problem is that `AutoConfig.from_pretrained()` for Qwen3.5 MoE returns a composite VLM config (with `model_type` like `"qwen3_5_moe"`), which is registered in the `VLM_REGISTRY` in `src/prime_rl/utils/vlm.py`. But when no `[model.vlm]` config is set, the single flag is `False`, so the code tries to load via `AutoModelForCausalLMPrimeRL` which doesn't recognize the composite config class.

The VLM path (`AutoModelForImageTextToText`) handles this config correctly, but the VLM path also triggers vision encoder freezing and FSDP sharding — which is wrong for text-only SFT.

## Expected behavior

- VLM architectures (those in `VLM_REGISTRY`) should route to the correct model class regardless of whether VLM training is configured
- Vision encoder freezing and FSDP sharding should only happen when `[model.vlm]` is explicitly set in config

## Relevant files

- `src/prime_rl/trainer/model.py` — `get_model()` and `setup_fsdp()` functions
- `src/prime_rl/utils/vlm.py` — VLM registry and utility functions
