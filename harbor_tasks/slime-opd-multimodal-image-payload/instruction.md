# Bug: On-Policy Distillation reward function ignores multimodal inputs

## Context

The `slime` framework supports on-policy distillation (OPD) via `slime/rollout/on_policy_distillation.py`. The `reward_func` in this module sends a payload to a remote reward model server to get teacher log-probabilities for distillation.

The `Sample` dataclass (in `slime/utils/types.py`) has a `multimodal_inputs` field that can contain images, videos, and other modality data. The utility `slime/utils/processing_utils.py` already provides `encode_image_for_rollout_engine()` to convert PIL images into base64-encoded strings suitable for the rollout/reward engine.

## Problem

When a `Sample` contains multimodal inputs (e.g., images from a vision-language task), the `reward_func` constructs its HTTP payload using only `sample.tokens` and sampling parameters. It completely ignores `sample.multimodal_inputs`, meaning the reward model server never receives the image data.

This causes the teacher model to evaluate multimodal prompts as if they were text-only, producing incorrect log-probabilities and degrading distillation quality for any vision-language workload.

## Expected Behavior

When a sample has multimodal image inputs, the reward function should encode and include them in the payload sent to the reward model server, so the teacher model can properly evaluate the full multimodal context.

## Relevant Files

- `slime/rollout/on_policy_distillation.py` — the `reward_func` that builds and sends the payload
- `slime/utils/processing_utils.py` — contains image encoding utilities
- `slime/utils/types.py` — defines `Sample` with `multimodal_inputs` field
