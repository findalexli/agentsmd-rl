# VLM GRPO Training Example for NPU Hardware

Create a VLM GRPO training example under `examples/vlm_npu/` for the AReaL framework targeting NPU hardware.

## Required Files

### `examples/vlm_npu/geometry3k_grpo.py`
Training script that:
- Imports from `areal` modules (not `realhf`)
- Imports `extract_boxed_content` and `grade_answer` from `mathruler.grader`
- Groups imports as: (1) standard library, (2) third-party, (3) internal areal/ modules
- Does NOT use wildcard imports

Implements three reward functions:

**`format_reward(predict_str: str) -> float`**
- Returns a reward value based on whether the prediction contains properly formatted reasoning tags and a boxed answer
- Uses multiline matching

**`acc_reward(predict_str: str, ground_truth: str) -> float`**
- Extracts answer from prediction using the grader's extraction function
- Grades with the grader's grading function and returns a reward value

**`geometry3k_reward_fn(prompt, completions, prompt_ids, completion_ids, answer, **kwargs) -> float`**
- Computes a combined score from accuracy and format rewards
- Uses a format weight parameter (see YAML config)
- Follows signature from AGENTS.md: `(prompt, completions, prompt_ids, completion_ids, **kwargs)`

The main function:
- Loads config via `load_expr_config` with `GRPOConfig`
- Loads processor/tokenizer from `config.tokenizer_path`
- Creates train/valid datasets via `get_custom_dataset` using `config.train_dataset` / `config.valid_dataset`
- Uses `PPOTrainer` with `VisionRLVRWorkflow` (reward_fn=geometry3k_reward_fn, enable_thinking=False)
- Saves generated outputs to `StatsLogger.get_log_path(config.stats_logger)/generated`

### `examples/vlm_npu/geometry3k_grpo.yaml`
YAML config with these required sections and keys:
- `experiment_name`, `trial_name`, `seed`, `enable_offload`, `total_train_epochs`, `tokenizer_path`
- `actor` section with model path, initialization settings, dropout, gradient checkpointing, dtype, optimizer, and group sizing
- `vllm` section with model, seed, dtype, max_model_len, gpu_memory_utilization
- `train_dataset` and `valid_dataset` with path, type, batch_size
- `gconfig` with n_samples, min/max_new_tokens, greedy, temperature
- `cluster` with n_nodes, n_gpus_per_node
- `allocation_mode` referencing vllm
- `rollout`, `saver`, `stats_logger`, `launcher` sections

### `examples/vlm_npu/geometry3k_grpo.sh`
Shell launcher that:
- Sets `USE_OPTIMIZED_MODEL=0`
- Runs the training script with the YAML config

### `examples/vlm_npu/README.md`
Documents:
- NPU hardware requirements (NPU, CPU cores, memory, network, storage)
- System configuration (vllm, torch_npu, AREA, CANN versions)
- Training results table with columns: Method, LogicVista, MathVision_mini, MathVista_mini, Avg
- Example rows showing Base Model, GRPO-GPU, GRPO-NPU results

## Repository Requirements

The repository must continue to pass all existing CI checks:
- All Python files parse without syntax errors
- All YAML files parse without errors
- No wildcard imports in areal/
- Ruff linting passes on areal/ and examples/
- Ruff format check passes on areal/ and examples/
- All C++ files pass clang-format check
- All JSON files are valid
- All Python files end with a newline
- No trailing whitespace in Python files
