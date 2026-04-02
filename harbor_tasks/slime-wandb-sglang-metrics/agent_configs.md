# Agent Config Files for slime-wandb-sglang-metrics

Repo: THUDM/slime
Commit: d4c4d3fb24d45c3cd12f47b64b30fc3301286778
Files found: 11


---
## .claude/skills/add-dynamic-filter/SKILL.md

```
   1 | ---
   2 | name: add-dynamic-filter
   3 | description: Guide for adding dynamic/filter hooks in slime rollout pipeline. Use when user wants sample-group selection during rollout, buffer filtering before training, or per-sample masking/processing hooks.
   4 | ---
   5 | 
   6 | # Add Dynamic Filter
   7 | 
   8 | Add filtering hooks in rollout and buffer stages while preserving sample-group contracts.
   9 | 
  10 | ## When to Use
  11 | 
  12 | Use this skill when:
  13 | 
  14 | - User asks to filter sample groups during dynamic sampling
  15 | - User asks to customize buffer extraction strategy
  16 | - User asks to mask/remove some rollout samples before training
  17 | - User asks to process all generated samples for logging/analysis
  18 | 
  19 | ## Step-by-Step Guide
  20 | 
  21 | ### Step 1: Pick the Correct Hook
  22 | 
  23 | - Dynamic sampling filter: `--dynamic-sampling-filter-path`
  24 | - Buffer filter: `--buffer-filter-path`
  25 | - Per-sample rollout filter: `--rollout-sample-filter-path`
  26 | - All-samples post process: `--rollout-all-samples-process-path`
  27 | 
  28 | ### Step 2: Implement the Function Signature
  29 | 
  30 | Dynamic sampling filter (called in `slime/rollout/sglang_rollout.py`):
  31 | 
  32 | ```python
  33 | def filter_function(args, samples, **kwargs):
  34 |     # return DynamicFilterOutput or bool
  35 | ```
  36 | 
  37 | Preferred return type:
  38 | 
  39 | ```python
  40 | from slime.rollout.filter_hub.base_types import DynamicFilterOutput
  41 | 
  42 | return DynamicFilterOutput(keep=True, reason=None)
  43 | ```
  44 | 
  45 | Buffer filter (called in `slime/rollout/data_source.py`):
  46 | 
  47 | ```python
  48 | def buffer_filter(args, rollout_id, buffer, num_samples):
  49 |     return selected_groups
  50 | ```
  51 | 
  52 | Rollout sample filter:
  53 | 
  54 | ```python
  55 | def rollout_sample_filter(args, samples):
  56 |     # modify sample.remove_sample in-place where needed
  57 | ```
  58 | 
  59 | All-samples process:
  60 | 
  61 | ```python
  62 | def process_all_samples(args, all_samples, data_source):
  63 |     ...
  64 | ```
  65 | 
  66 | ### Step 3: Preserve Group Structure
  67 | 
  68 | - Keep `list[list[Sample]]` structure intact where required.
  69 | - Do not flatten sample groups unless downstream path expects flattened samples.
  70 | - For sample removal, prefer `sample.remove_sample=True` over deleting objects.
  71 | 
  72 | ### Step 4: Wire and Validate
  73 | 
  74 | Example wiring:
  75 | 
  76 | ```bash
  77 | --dynamic-sampling-filter-path slime.rollout.filter_hub.dynamic_sampling_filters.check_reward_nonzero_std
  78 | --buffer-filter-path <module>.buffer_filter
  79 | --rollout-sample-filter-path <module>.rollout_sample_filter
  80 | --rollout-all-samples-process-path <module>.process_all_samples
  81 | ```
  82 | 
  83 | ### Step 5: Measure Side Effects
  84 | 
  85 | - Check final sample count remains aligned with `rollout_batch_size` expectations.
  86 | - Verify drop reasons are surfaced in rollout metrics when dynamic filter is used.
  87 | - Validate training still receives valid loss masks/rewards after filtering.
  88 | 
  89 | ## Common Mistakes
  90 | 
  91 | - Returning wrong container type for buffer filter
  92 | - Dropping samples by deletion instead of mask flagging
  93 | - Losing sample-group alignment in group-RM setup
  94 | - Adding expensive logic in hot filtering paths
  95 | 
  96 | ## Reference Locations
  97 | 
  98 | - Dynamic filter types: `slime/rollout/filter_hub/base_types.py`
  99 | - Dynamic filter example: `slime/rollout/filter_hub/dynamic_sampling_filters.py`
 100 | - Rollout generation hook points: `slime/rollout/sglang_rollout.py`
 101 | - Buffer filter hook point: `slime/rollout/data_source.py`
```


---
## .claude/skills/add-eval-dataset-config/SKILL.md

```
   1 | ---
   2 | name: add-eval-dataset-config
   3 | description: Guide for adding and validating evaluation dataset configuration in slime. Use when user wants to configure eval datasets via --eval-config or --eval-prompt-data, add per-dataset overrides, or customize evaluation rollout behavior.
   4 | ---
   5 | 
   6 | # Add Eval Dataset Config
   7 | 
   8 | Configure evaluation datasets in slime with explicit dataset-level overrides and predictable runtime behavior.
   9 | 
  10 | ## When to Use
  11 | 
  12 | Use this skill when:
  13 | 
  14 | - User asks to add evaluation datasets for periodic eval
  15 | - User asks to migrate from `--eval-prompt-data` to structured `--eval-config`
  16 | - User asks for per-dataset eval overrides (sampling params, keys, rm_type, metadata)
  17 | 
  18 | ## Step-by-Step Guide
  19 | 
  20 | ### Step 1: Choose Config Entry Method
  21 | 
  22 | Supported inputs:
  23 | 
  24 | - Structured config file: `--eval-config <yaml>`
  25 | - Legacy CLI pairs: `--eval-prompt-data <name1> <path1> <name2> <path2> ...`
  26 | 
  27 | If `--eval-interval` is set, eval datasets must be configured.
  28 | 
  29 | ### Step 2: Build YAML with Required Fields
  30 | 
  31 | Each dataset needs at least:
  32 | 
  33 | - `name`
  34 | - `path`
  35 | 
  36 | Example:
  37 | 
  38 | ```yaml
  39 | eval:
  40 |   defaults:
  41 |     n_samples_per_eval_prompt: 1
  42 |     temperature: 0.7
  43 |     top_p: 1.0
  44 |   datasets:
  45 |     - name: aime
  46 |       path: /path/to/aime.jsonl
  47 |       rm_type: math
  48 |       input_key: prompt
  49 |       label_key: answer
  50 |       metadata_overrides:
  51 |         split: test
  52 | ```
  53 | 
  54 | ### Step 3: Understand Override Priority
  55 | 
  56 | `slime/utils/eval_config.py` resolves fields in this order:
  57 | 
  58 | 1. Dataset-level values in `eval.datasets[*]`
  59 | 2. `eval.defaults`
  60 | 3. CLI args fallback (for example eval_* or rollout_* fields)
  61 | 
  62 | Common overridable fields include:
  63 | 
  64 | - Runtime: `n_samples_per_eval_prompt`, `temperature`, `top_p`, `top_k`, `max_response_len`
  65 | - Sample keys: `input_key`, `label_key`, `tool_key`, `metadata_key`
  66 | - Extra: `rm_type`, `custom_generate_function_path`, `metadata_overrides`
  67 | 
  68 | ### Step 4: Wire Eval Function if Needed
  69 | 
  70 | By default, eval uses `--eval-function-path` (defaults to rollout function path).
  71 | Use a separate eval function when inference/eval behavior must differ from training rollout.
  72 | 
  73 | ### Step 5: Validate Parsing and Runtime
  74 | 
  75 | - Start with config parsing sanity by running a short launch command.
  76 | - Confirm dataset entries are loaded into `args.eval_datasets`.
  77 | - Verify output keys match eval logging/metrics expectations.
  78 | 
  79 | ## Common Mistakes
  80 | 
  81 | - Missing `name` in dataset entries
  82 | - Odd-length `--eval-prompt-data` pairs
  83 | - Setting `--eval-interval` without any eval dataset
  84 | - Mixing reward dict outputs without `eval_reward_key` configuration
  85 | 
  86 | ## Reference Locations
  87 | 
  88 | - Eval config model: `slime/utils/eval_config.py`
  89 | - Eval config resolution: `slime/utils/arguments.py`
  90 | - Eval rollout path: `slime/rollout/sglang_rollout.py`
  91 | - Customization docs: `docs/en/get_started/customization.md`
```


---
## .claude/skills/add-reward-function/SKILL.md

```
   1 | ---
   2 | name: add-reward-function
   3 | description: Guide for adding a custom reward function in slime and wiring it through --custom-rm-path (and optional reward post-processing). Use when user wants new reward logic, remote/service reward integration, or task-specific reward shaping.
   4 | ---
   5 | 
   6 | # Add Reward Function
   7 | 
   8 | Implement custom reward logic and connect it to slime rollout/training safely.
   9 | 
  10 | ## When to Use
  11 | 
  12 | Use this skill when:
  13 | 
  14 | - User asks to add new reward computation logic
  15 | - User asks to integrate an external reward service
  16 | - User asks to customize reward normalization/post-processing
  17 | 
  18 | ## Step-by-Step Guide
  19 | 
  20 | ### Step 1: Choose Reward Mode
  21 | 
  22 | Pick one of these:
  23 | 
  24 | - Single-sample mode (`--group-rm` disabled): custom function gets one `Sample`
  25 | - Group/batch mode (`--group-rm` enabled): custom function gets `list[Sample]`
  26 | 
  27 | `slime.rollout.rm_hub.__init__.py` calls your function via `--custom-rm-path`.
  28 | 
  29 | ### Step 2: Create Reward Module
  30 | 
  31 | Create `slime/rollout/rm_hub/<your_rm>.py`.
  32 | 
  33 | Supported signatures:
  34 | 
  35 | ```python
  36 | async def custom_rm(args, sample):
  37 |     return float_reward_or_reward_dict
  38 | ```
  39 | 
  40 | ```python
  41 | async def custom_rm(args, samples):
  42 |     return list_of_rewards
  43 | ```
  44 | 
  45 | If using group mode, return one reward per sample in input order.
  46 | 
  47 | ### Step 3: Keep Reward Type Consistent
  48 | 
  49 | - Return scalar numeric rewards unless your pipeline explicitly uses keyed rewards.
  50 | - If using reward dicts, ensure downstream `reward_key` / `eval_reward_key` is configured.
  51 | - Keep exceptions explicit for invalid metadata instead of silently returning zeros.
  52 | 
  53 | ### Step 4: Optional Reward Post-Processing
  54 | 
  55 | To customize normalization/shaping before advantage computation, add:
  56 | 
  57 | ```python
  58 | def post_process_rewards(args, samples):
  59 |     # return (raw_rewards, processed_rewards)
  60 |     ...
  61 | ```
  62 | 
  63 | Wire with:
  64 | 
  65 | ```bash
  66 | --custom-reward-post-process-path <module>.post_process_rewards
  67 | ```
  68 | 
  69 | This hook is consumed in `slime/ray/rollout.py`.
  70 | 
  71 | ### Step 5: Wire and Validate
  72 | 
  73 | Use:
  74 | 
  75 | ```bash
  76 | --custom-rm-path slime.rollout.rm_hub.<your_rm>.custom_rm
  77 | ```
  78 | 
  79 | ## Common Mistakes
  80 | 
  81 | - Returning wrong output shape in group mode
  82 | - Mixing scalar rewards and reward dicts without `reward_key` config
  83 | - Doing blocking network calls without async handling
  84 | - Forgetting to validate reward behavior on truncated/failed samples
  85 | 
  86 | ## Reference Locations
  87 | 
  88 | - Reward dispatch: `slime/rollout/rm_hub/__init__.py`
  89 | - Reward post-process hook: `slime/ray/rollout.py`
  90 | - Customization docs: `docs/en/get_started/customization.md`
```


---
## .claude/skills/add-rollout-function/SKILL.md

```
   1 | ---
   2 | name: add-rollout-function
   3 | description: Guide for adding a new rollout function in slime and wiring it through --rollout-function-path. Use when user wants to implement custom rollout data generation logic, custom train/eval rollout outputs, or migrate from the default sglang rollout path.
   4 | ---
   5 | 
   6 | # Add Rollout Function
   7 | 
   8 | Implement a custom rollout function and integrate it safely with slime training/eval flow.
   9 | 
  10 | ## When to Use
  11 | 
  12 | Use this skill when:
  13 | 
  14 | - User asks to add a new rollout task or rollout generation function
  15 | - User asks to replace default `slime.rollout.sglang_rollout.generate_rollout`
  16 | - User asks to customize train/eval data generation behavior
  17 | 
  18 | ## Step-by-Step Guide
  19 | 
  20 | ### Step 1: Choose the Right Starting Point
  21 | 
  22 | Start from one of these references:
  23 | 
  24 | - Async RL-style rollout: `slime/rollout/sglang_rollout.py`
  25 | - Simple SFT-style rollout: `slime/rollout/sft_rollout.py`
  26 | 
  27 | If the task needs engine-based async generation and rewards, use the sglang path as base.
  28 | If the task is file/buffer-driven and simple, use sft path as base.
  29 | 
  30 | ### Step 2: Create the New Rollout Module
  31 | 
  32 | Create a new file, for example: `slime/rollout/<your_rollout>.py`
  33 | 
  34 | Required callable signature:
  35 | 
  36 | ```python
  37 | def generate_rollout(args, rollout_id, data_source, evaluation=False) -> RolloutFnTrainOutput | RolloutFnEvalOutput:
  38 |     ...
  39 | ```
  40 | 
  41 | Return types are defined in `slime/rollout/base_types.py`.
  42 | 
  43 | ### Step 3: Implement Train and Eval Branches Explicitly
  44 | 
  45 | - For training (`evaluation=False`), return `RolloutFnTrainOutput(samples=..., metrics=...)`
  46 | - For evaluation (`evaluation=True`), return `RolloutFnEvalOutput(data=..., metrics=...)`
  47 | 
  48 | Minimal skeleton:
  49 | 
  50 | ```python
  51 | from slime.rollout.base_types import RolloutFnTrainOutput, RolloutFnEvalOutput
  52 | 
  53 | 
  54 | def generate_rollout(args, rollout_id, data_source, evaluation=False):
  55 |     if evaluation:
  56 |         result = {
  57 |             "custom_eval": {
  58 |                 "rewards": [],
  59 |                 "truncated": [],
  60 |                 "samples": [],
  61 |             }
  62 |         }
  63 |         return RolloutFnEvalOutput(data=result)
  64 | 
  65 |     groups = data_source.get_samples(args.rollout_batch_size)
  66 |     # fill Sample fields needed by training: tokens/response_length/reward/status (+ loss_mask when needed)
  67 |     return RolloutFnTrainOutput(samples=groups)
  68 | ```
  69 | 
  70 | ### Step 4: Keep Data Contract Compatible
  71 | 
  72 | For each generated sample, ensure required training fields are populated consistently with your objective:
  73 | 
  74 | - `tokens`
  75 | - `response_length`
  76 | - `reward` (or reward dict if your setup uses keyed rewards)
  77 | - `status`
  78 | 
  79 | If partial rollout or masking logic is involved, keep `loss_mask` semantics consistent with existing behavior.
  80 | 
  81 | ### Step 5: Wire Through Arguments
  82 | 
  83 | Set your function path via CLI:
  84 | 
  85 | ```bash
  86 | --rollout-function-path slime.rollout.<your_rollout>.generate_rollout
  87 | ```
  88 | 
  89 | The default and signature expectation are documented in:
  90 | 
  91 | - `slime/utils/arguments.py`
  92 | - `docs/en/get_started/customization.md`
  93 | 
  94 | ## Common Mistakes
  95 | 
  96 | - Returning raw Python lists/dicts with mismatched schema in custom path
  97 | - Implementing only training branch and forgetting evaluation branch
  98 | - Generating samples without required fields (`tokens`, `response_length`, `reward`, `status`)
  99 | - Using blocking-heavy logic in high-frequency rollout paths without batching/concurrency control
 100 | 
 101 | ## Reference Locations
 102 | 
 103 | - Default rollout: `slime/rollout/sglang_rollout.py`
 104 | - Simple custom example: `slime/rollout/sft_rollout.py`
 105 | - Output dataclasses: `slime/rollout/base_types.py`
 106 | - Wiring/loading: `slime/ray/rollout.py`
 107 | - Argument definition: `slime/utils/arguments.py`
 108 | - Customization docs: `docs/en/get_started/customization.md`
```


---
## .claude/skills/add-tests-and-ci/SKILL.md

```
   1 | ---
   2 | name: add-tests-and-ci
   3 | description: Guide for adding or updating slime tests and CI wiring. Use when tasks require new test cases, CI registration, test matrix updates, or workflow template changes.
   4 | ---
   5 | 
   6 | # Add Tests and CI
   7 | 
   8 | Add reliable tests and integrate them with slime CI flow.
   9 | 
  10 | ## When to Use
  11 | 
  12 | Use this skill when:
  13 | 
  14 | - User asks to add tests for new behavior
  15 | - User asks to fix or update existing tests in `tests/`
  16 | - User asks to update CI workflow behavior
  17 | - User asks how to run targeted checks before PR
  18 | 
  19 | ## Step-by-Step Guide
  20 | 
  21 | ### Step 1: Pick the Right Test Pattern
  22 | 
  23 | - Follow existing naming: `tests/test_<feature>.py`
  24 | - Start from nearest existing test file for your model/path
  25 | - Keep test scope small and behavior-focused
  26 | 
  27 | ### Step 2: Keep CI Compatibility
  28 | 
  29 | When creating CI-discoverable tests, ensure top-level constants and conventions match repository patterns (including `NUM_GPUS = <N>` where expected).
  30 | 
  31 | ### Step 3: Run Local Validation
  32 | 
  33 | - Run the exact existing test files you changed, if any.
  34 | - Run repository-wide checks only when they are already part of the task or workflow.
  35 | - Avoid documenting placeholder test commands that may not exist in the current tree.
  36 | 
  37 | ### Step 4: Update Workflow Template Correctly
  38 | 
  39 | For CI workflow changes:
  40 | 
  41 | 1. Edit `.github/workflows/pr-test.yml.j2`
  42 | 2. Regenerate workflows:
  43 | 
  44 | ```bash
  45 | python .github/workflows/generate_github_workflows.py
  46 | ```
  47 | 
  48 | 3. Commit both template and generated workflow files
  49 | 
  50 | ### Step 5: Provide Verifiable PR Notes
  51 | 
  52 | Include:
  53 | 
  54 | - Which tests were added/changed
  55 | - Exact commands executed
  56 | - GPU assumptions for each test path
  57 | - Why this coverage protects against regression
  58 | 
  59 | ## Common Mistakes
  60 | 
  61 | - Editing generated workflow file only
  62 | - Adding tests without following existing constants/conventions
  63 | - Making tests too large or non-deterministic
  64 | - Skipping local validation and relying only on remote CI
  65 | 
  66 | ## Reference Locations
  67 | 
  68 | - Pytest config: `pyproject.toml`
  69 | - Tests: `tests/`
  70 | - CI template: `.github/workflows/pr-test.yml.j2`
  71 | - CI guide: `docs/en/developer_guide/ci.md`
```


---
## README.md

```
   1 | # slime
   2 | 
   3 | [中文版](./README_zh.md)
   4 | 
   5 | [![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat)](https://thudm.github.io/slime/)
   6 | [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/THUDM/slime)
   7 | 
   8 | **slime** is an LLM post-training framework for RL scaling, providing two core capabilities:
   9 | 
  10 | 1.  **High-Performance Training**: Supports efficient training in various modes by connecting Megatron with SGLang;
  11 | 2.  **Flexible Data Generation**: Enables arbitrary training data generation workflows through custom data generation interfaces and server-based engines.
  12 | 
  13 | slime is the RL-framework behind [GLM-5](https://z.ai/blog/glm-5), [GLM-4.7](https://z.ai/blog/glm-4.7), [GLM-4.6](https://z.ai/blog/glm-4.6), [GLM-4.5](https://z.ai/blog/glm-4.5) and apart from models from Z.ai, we also supports the following models:
  14 | - Qwen3 series (Qwen3Next, Qwen3MoE, Qwen3), Qwen2.5 series;
  15 | - DeepSeek V3 series (DeepSeek V3, V3.1, DeepSeek R1);
  16 | - Llama 3.
  17 | 
  18 | ## Blogs
  19 | 
  20 | - Our vision: [slime: An SGLang-Native Post-Training Framework for RL Scaling](https://lmsys.org/blog/2025-07-09-slime/).
  21 | - Our ideas on agentic training: [Agent-Oriented Design: An Asynchronous and Decoupled Framework for Agentic RL](https://www.notion.so/Agent-Oriented-Design-An-Asynchronous-and-Decoupled-Framework-for-Agentic-RL-2278e692d081802cbdd5d37cef76a547)
  22 | - v0.1.0 release note: [v0.1.0: Redefining High-Performance RL Training Frameworks](https://thudm.github.io/slime/blogs/release_v0.1.0.html)
  23 | 
  24 | ## Table of Contents
  25 | 
  26 | - [Architecture Overview](#architecture-overview)
  27 | - [Quick Start](#quick-start)
  28 | - [Projects Built with slime](#projects-built-with-slime)
  29 | - [Arguments Walkthrough](#arguments-walkthrough)
  30 | - [Developer Guide](#developer-guide)
  31 | - [FAQ & Acknowledgements](#faq--acknowledgements)
  32 | 
  33 | ## Architecture Overview
  34 | 
  35 | ![arch](./imgs/arch.png)
  36 | 
  37 | **Module Descriptions**:
  38 | 
  39 | - **training (Megatron)**: Responsible for the main training process, reads data from the Data Buffer, and synchronizes parameters to the rollout module after training.
  40 | - **rollout (SGLang + router)**: Generates new data (including rewards/verifier outputs) and stores it in the Data Buffer.
  41 | - **data buffer**: A bridge module that manages prompt initialization, custom data, and rollout generation methods.
  42 | 
  43 | ## Quick Start
  44 | 
  45 | For a comprehensive quick start guide covering environment setup, data preparation, training startup, and key code analysis, please refer to:
  46 | - [Quick Start Guide](./docs/en/get_started/quick_start.md)
  47 | 
  48 | We also provide examples for some use cases not covered in the quick start guide; please check [examples](examples/).
  49 | 
  50 | ## Projects Built upon slime
  51 | 
  52 | slime has powered several novel research projects and production systems. Here are some notable examples:
  53 | 
  54 | ### 🦞 OpenClaw-RL: Train a Personalized Clawbot Simply by Talking to It
  55 | 
  56 | [**OpenClaw-RL**](https://github.com/Gen-Verse/OpenClaw-RL) is an RL server for personalized OpenClaw agents. It hosts the OpenClaw model and improves it from prior conversations across deployments, while slime's asynchronous RL infrastructure prevents training from interfering with API serving. It supports two automatic optimization methods: GRPO with binary feedback inferred from subsequent states, and on-policy distillation that extracts hindsight hints from later feedback for the current policy.
  57 | 
  58 | ### ⚛️ P1: Mastering Physics Olympiads with Reinforcement Learning
  59 | 
  60 | [**P1**](https://prime-rl.github.io/P1/) is a family of open-source physics reasoning models trained entirely through reinforcement learning. P1 leverages slime as the RL post training framework, and introduces a multi-stage RL training algorithm that progressively enhances reasoning ability through adaptive learnability adjustment and stabilization mechanisms. Enpowered by this training paradigm, P1 delivers breakthrough performance in open-source physics reasoning.
  61 | 
  62 | ### 📈RLVE: Scaling LM RL with Adaptive Verifiable Environments
  63 | 
  64 | [**RLVE**](https://github.com/Zhiyuan-Zeng/RLVE) introduces an approach using verifiable environments that procedurally generate problems and provide algorithmically verifiable rewards, to scale up RL for language models (LMs). With joint training across 400 verifiable environments, RLVE enables each environment to dynamically adapt its problem difficulty distribution to the policy model's capabilities as training progresses.
  65 | 
  66 | ### ⚡ TritonForge: Agentic RL Training Framework for Kernel Generation
  67 | 
  68 | [**TritonForge**](https://github.com/RLsys-Foundation/TritonForge) leverages slime's SFT & RL capabilities to train LLMs that automatically generate optimized GPU kernels. By using a two-stage training approach—supervised fine-tuning followed by reinforcement learning with multi-turn compilation feedback—TritonForge achieves remarkable results in converting PyTorch operations into high-performance Triton kernels.
  69 | 
  70 | ### 🚀 APRIL: Accelerating RL Training with Active Partial Rollouts
  71 | 
  72 | [**APRIL**](https://github.com/RLsys-Foundation/APRIL) introduces a system-level optimization that seamlessly integrates with slime to accelerate the rollout generation phase in RL training. By intelligently over-provisioning requests and actively managing partial completions, APRIL addresses the long-tail generation bottleneck that typically consumes over 90% of RL training time.
  73 | 
  74 | ### 🏟️ qqr: Scaling Open-Ended Agents with ArenaRL & MCP
  75 | 
  76 | [**qqr**](https://github.com/Alibaba-NLP/qqr) (a.k.a. hilichurl) is a lightweight extension for slime designed to evolve open-ended agents. It implements the **ArenaRL** algorithm to tackle discriminative collapse through tournament-based relative ranking (**e.g., Seeded Single-Elimination, Round-Robin**) and seamlessly integrates the **Model Context Protocol (MCP)**. qqr leverages slime's high-throughput training capabilities to enable scalable, distributed evolution of agents in standardized, decoupled tool environments.
  77 | 
  78 | These projects showcase slime's versatility—from training code-generation models to optimizing RL training systems—making it a powerful foundation for both research and production deployments.
  79 | 
  80 | ## Arguments Walkthrough
  81 | 
  82 | Arguments in slime are divided into three categories:
  83 | 
  84 | 1.  **Megatron arguments**: slime reads all arguments in Megatron. You can configure Megatron by passing arguments like `--tensor-model-parallel-size 2`.
  85 | 2.  **SGLang arguments**: All arguments for the installed SGLang are supported. These arguments must be prefixed with `--sglang-`. For example, `--mem-fraction-static` should be passed as `--sglang-mem-fraction-static`.
  86 | 3.  **slime-specific arguments**: Please refer to: [slime/utils/arguments.py](slime/utils/arguments.py)
  87 | 
  88 | For complete usage instructions, please refer to the [Usage Documentation](docs/en/get_started/usage.md).
  89 | 
  90 | ## Developer Guide
  91 | 
  92 | - **Contributions are welcome\!** If you have suggestions for new features, performance tuning, or feedback on user experience, feel free to submit an Issue or PR 😊
  93 | 
  94 | - Use [pre-commit](https://pre-commit.com/) to ensure code style consistency for your commits:
  95 | 
  96 | ```bash
  97 | apt install pre-commit -y
  98 | pre-commit install
  99 | 
 100 | # run pre-commit to ensure code style consistency
 101 | pre-commit run --all-files --show-diff-on-failure --color=always
 102 | ```
 103 | 
 104 | - For debugging tips, please refer to the [Debugging Guide](docs/en/developer_guide/debug.md)
 105 | 
 106 | ## FAQ & Acknowledgements
 107 | 
 108 | - For frequently asked questions, please see the [Q\&A](docs/en/get_started/qa.md)
 109 | - Special thanks to the following projects & communities: SGLang, Megatron‑LM, mbridge, OpenRLHF, veRL, Pai-Megatron-Patch and others.
 110 | - To quote slime, please use:
 111 | 
 112 | ```bibtex
 113 | @misc{slime_github,
 114 |   author       = {Zilin Zhu and Chengxing Xie and Xin Lv and slime Contributors},
 115 |   title        = {slime: An LLM post-training framework for RL Scaling},
 116 |   year         = {2025},
 117 |   howpublished = {\url{https://github.com/THUDM/slime}},
 118 |   note         = {GitHub repository. Corresponding author: Xin Lv},
 119 |   urldate      = {2025-06-19}
 120 | }
 121 | ```
```
