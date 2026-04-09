# VLM Training on NPU

## Problem

AReaL currently provides VLM (Vision Language Model) training examples only for GPU devices. There is no official example demonstrating how to train VLMs on NPU (e.g., Ascend) using AReaL and vllm-ascend. This makes NPU usage harder to adopt, debug, and reproduce.

## Expected Behavior

Add a complete NPU training example under `examples/vlm_npu/` that includes:
- A Python training script (`geometry3k_grpo.py`) with reward functions for Geometry3K GRPO training
- A shell launcher script (`geometry3k_grpo.sh`) with NPU-specific environment settings
- A YAML configuration file (`geometry3k_grpo.yaml`) for Qwen2.5-VL-3B training
- A README documenting hardware requirements, system configuration, and results

## Files to Look At

- `examples/vlm_npu/` — new directory for NPU training example (does not exist yet)
- `examples/` — existing GPU examples to follow as reference patterns
- `areal/workflow/vision_rlvr.py` — VisionRLVRWorkflow used by the training script
- `AGENTS.md` — project conventions for code style, imports, and reward function signatures
