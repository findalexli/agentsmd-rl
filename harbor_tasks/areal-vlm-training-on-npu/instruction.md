# VLM Training on NPU

## Problem

AReaL currently provides VLM (Vision Language Model) training examples only for GPU devices. There is no official example demonstrating how to train VLMs on NPU (e.g., Ascend) using AReaL and vllm-ascend. This makes NPU usage harder to adopt, debug, and reproduce.

## Expected Behavior

Add a complete NPU training example under `examples/vlm_npu/` that includes:

### 1. Python training script (`geometry3k_grpo.py`)

The script must:
- Import `extract_boxed_content` and `grade_answer` from `mathruler.grader`
- Define `format_reward(predict_str: str) -> float` that returns `1.0` when the prediction matches the regex pattern `r".*\\blacksquare.*\\boxed\{.*\}.*"` (re.DOTALL), otherwise `0.0`
- Define `acc_reward(predict_str: str, ground_truth: str) -> float` using `extract_boxed_content` and `grade_answer`
- Define `geometry3k_reward_fn(prompt, completions, prompt_ids, completion_ids, answer, **kwargs)` that computes a weighted score combining format and accuracy rewards (format weight: 0.1)
- Use `VisionRLVRWorkflow` from `areal.workflow.vision_rlvr` for training
- Follow the reward function signature convention from AGENTS.md: `(prompt, completions, prompt_ids, completion_ids, **data)`
- Have no wildcard imports (e.g., no `from X import *`)

### 2. Shell launcher script (`geometry3k_grpo.sh`)

The script must:
- Set environment variable `USE_OPTIMIZED_MODEL=0` for NPU compatibility
- Launch training using `python -m areal.launcher.local`
- Reference the Python script at `examples/vlm_npu/geometry3k_grpo.py`
- Reference the YAML config at `examples/vlm_npu/geometry3k_grpo.yaml`

### 3. YAML configuration file (`geometry3k_grpo.yaml`)

The config must be valid YAML and include these required top-level keys:
- `experiment_name`: string identifier for the experiment
- `trial_name`: string identifier for the trial
- `actor`: configuration object with `path` specifying the model (use `Qwen/Qwen2.5-VL-3B-Instruct`)
- `vllm`: configuration object with `model` specifying the inference backend settings
- `train_dataset`: configuration with `path` and `type: rl`
- `valid_dataset`: configuration with `path` and `type: rl`
- `gconfig`: generation config with `n_samples`, `min_new_tokens`, `max_new_tokens`, `temperature`
- `cluster`: cluster configuration with `n_nodes`, `n_gpus_per_node`, `fileroot`, `name_resolve`
- `allocation_mode`: string referencing vllm allocation (NPU uses vllm-ascend), e.g., `vllm:d4p1t1+d4p1t1`
- `rollout`: rollout configuration with `experiment_name`, `trial_name`, `max_concurrent_rollouts`
- `saver`: checkpoint saver configuration with `experiment_name`, `trial_name`, `fileroot`, `freq_epochs`

### 4. README (`README.md`)

The README must document:
- Hardware requirements (mention "NPU" specifically)
- System configuration details (vllm version, CANN version, etc.)
- Training results in a markdown table format with benchmark names as columns (e.g., LogicVista, MathVision_mini, MathVista_mini) and rows for Base Model, GRPO-GPU, and GRPO-NPU

## Files to Look At

- `examples/vlm_npu/` — new directory for NPU training example (does not exist yet)
- `examples/` — existing GPU examples to follow as reference patterns
- `areal/workflow/vision_rlvr.py` — VisionRLVRWorkflow used by the training script
- `AGENTS.md` — project conventions for code style, imports, and reward function signatures
