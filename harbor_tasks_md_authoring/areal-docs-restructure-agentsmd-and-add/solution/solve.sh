#!/usr/bin/env bash
set -euo pipefail

cd /workspace/areal

# Idempotency guard
if grep -qF "1. **Inference engines (`areal/engine/`)** \u2013 Handle async generation and weight " "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -32,20 +32,20 @@ When unsure, leave a `TODO(agent)` comment and note the constraint in your respo
     helpers.
   - `areal/core/` — Async orchestration primitives for task runners, remote inference,
     and workflow execution.
-  - `areal/dataset/` — Stateful dataset loaders and utilities that feed rollout jobs
-    safely.
-  - `areal/engine/` — Training/inference backends (FSDP2, Megatron, PPO actors, remote
-    adapters).
+  - `areal/dataset/` — Stateful dataset loaders (GSM8K, Geometry3K, CLEVR, HH-RLHF,
+    TORL, etc.) and utilities that feed rollout jobs safely.
+  - `areal/engine/` — Training backends (FSDP2, Megatron, PPO, SFT, reward modeling) and
+    inference adapters (SGLang, vLLM remote engines).
   - `areal/experimental/` — Prototype engines/workflows that evolve quickly; expect
     breaking changes.
-  - `areal/launcher/` — Launch specs for local, Ray, and Slurm clusters plus container
-    guidance.
+  - `areal/launcher/` — Launch specs for local, Ray, and Slurm clusters, plus
+    SGLang/vLLM inference server launchers and container guidance.
   - `areal/models/` — Model-specific adapters (Megatron-Core layers, Transformers
     wrappers, custom heads).
   - `areal/platforms/` — Hardware/platform abstractions for CPU/GPU/NPU runtimes and
     device adapters.
-  - `areal/reward/` — Built-in reward functions, math parsers, and helpers (wrap slow
-    logic with AsyncRewardWrapper).
+  - `areal/reward/` — Built-in reward functions (GSM8K, Geometry3K, CLEVR, etc.), math
+    parsers, and helpers; wrap slow logic with `AsyncRewardWrapper`.
   - `areal/scheduler/` — Placement and allocation policies aligned with launcher
     configs.
   - `areal/tests/` — Focused unit/integration suites (many require GPUs or mocked
@@ -55,8 +55,9 @@ When unsure, leave a `TODO(agent)` comment and note the constraint in your respo
     package.
   - `areal/utils/` — Cross-cutting helpers for logging, tensor ops, stats tracking,
     checkpoints, and recovery.
-  - `areal/workflow/` — Concrete rollout agents (`multi_turn`, `rlvr`, `vision_rlvr`)
-    implementing `RolloutWorkflow`.
+  - `areal/workflow/` — Concrete rollout agents implementing `RolloutWorkflow`:
+    multi-turn, RLVR, vision RLVR workflows, plus `openai_agent/` for OpenAI Agent-style
+    implementations.
 - `assets/` — Figures and other static assets referenced across docs and blogs.
 - `benchmark/` — Regression baselines, benchmark snapshots, and reference metrics (e.g.,
   `verl_v0_3_0_post1_*`).
@@ -67,16 +68,17 @@ When unsure, leave a `TODO(agent)` comment and note the constraint in your respo
   reference generators.
 - `evaluation/` — Offline scoring pipelines (math, code, Elo) and shared
   evaluators/utilities.
-- `examples/` — End-to-end wiring scripts for math, RLHF, VLM, multi-turn, search
-  agents, and launcher recipes.
+- `examples/` — End-to-end training scripts and launcher recipes for math reasoning,
+  multi-turn conversations, VLM, RLHF alignment, agent-based workflows, LoRA
+  fine-tuning, SkyPilot deployment, and more.
 - `functioncall/` — Tool-calling scaffolding reused by workflows and evaluation
   harnesses.
 - `notebook/` — Reference notebooks (outputs stripped via pre-commit) for quick
   experimentation.
 - `patch/` — In-tree patches applied to third-party dependencies (e.g., SGLang
   hotfixes).
-- `realhf/` — Legacy integrations kept read-only; do **not** modify or import in new
-  code.
+- `realhf/` — **Legacy, read-only.** Do not modify or import; migrate any `realhf` call
+  sites to `areal/` equivalents. Flag lingering usage in reviews/issues.
 - `recipe/` — Deployment recipes and higher-level orchestration configs per target
   environment.
 
@@ -98,17 +100,7 @@ When unsure, leave a `TODO(agent)` comment and note the constraint in your respo
   hook) before submitting; keep doc edits aligned with the Jupyter Book structure in
   `docs/`.
 
-## Legacy `realhf/` (read-only)
-
-- `realhf/` remains only for archival context. The package build explicitly excludes it
-  via `pyproject.toml`.
-- Do **not** modify files under `realhf/`, and avoid importing them in new code. Treat
-  any dependency on these modules as tech debt.
-- When you encounter a `realhf` call site, prefer migrating the logic to the matching
-  `areal/` module or partner with maintainers to port it.
-- Flag lingering `realhf` usage in reviews/issues so we can track and eliminate it.
-
-### Code style & patterns
+## Code style & patterns
 
 - **Typing & dataclasses**: Prefer explicit type hints and reuse existing dataclasses in
   `areal/api/cli_args.py` when extending configs. When adding new configuration options,
@@ -137,14 +129,22 @@ When unsure, leave a `TODO(agent)` comment and note the constraint in your respo
 
 ## Core concepts & extension points
 
-1. **Rollout workflows (`areal/api/workflow_api.py`)** – Implement
+1. **Trainer (`areal/experimental/trainer/`)** – High-level training orchestrator. Use
+   `PPOTrainer` for RL training or `SFTTrainer` for supervised fine-tuning. See
+   `examples/math/gsm8k_rl.py` for a complete example:
+   ```python
+   from areal.experimental.trainer import PPOTrainer
+   with PPOTrainer(config, train_dataset, valid_dataset) as trainer:
+       trainer.train(workflow="areal.workflow.rlvr.RLVRWorkflow", ...)
+   ```
+1. **Rollout workflows (`areal/workflow/`, `areal/api/workflow_api.py`)** – Implement
    `RolloutWorkflow.arun_episode`. Use helpers like `concat_padded_tensors` and respect
-   shape `[batch, seq_len, …]`.
-1. **Inference engines (`areal/engine/sglang_remote.py`,
-   `areal/engine/vllm_remote.py`)** – Handle async generation and weight updates.
-   Interact with workflows via `InferenceEngine.agenerate`.
-1. **Training engines (`areal/engine/ppo/actor.py`, `areal/engine/fsdp_engine.py`)** –
-   Consume rollout tensors, run PPO/GRPO updates, broadcast weight versions.
+   shape `[batch, seq_len, …]`. Pass workflow class path to `trainer.train()`.
+1. **Inference engines (`areal/engine/`)** – Handle async generation and weight updates.
+   Interact with workflows via `InferenceEngine.agenerate`. Includes SGLang/vLLM remote
+   adapters.
+1. **Training engines (`areal/engine/`)** – Consume rollout tensors, run PPO/GRPO
+   updates, broadcast weight versions. Includes FSDP2 and Megatron backends.
 1. **Rewards (`areal/api/reward_api.py`, `areal/reward/`)** – Wrap blocking reward code
    in `AsyncRewardWrapper`. Standard signature:
    `(prompt, completions, prompt_ids, completion_ids, **data)`.
@@ -175,8 +175,8 @@ Reference docs:
 - Persist transcripts under `{dump_dir}/{engine.get_version()}/` (follow the
   `multi_turn` implementation) when debugging is enabled.
 - Update whichever entry script or launcher references the workflow (e.g.,
-  `examples/multi-turn-math/train.py`, configs in `examples/**/conf/`, or CLI glue) so
-  Hydra can import the new module.
+  `examples/multi-turn-math/gsm8k_rl_mt.py`, configs in `examples/**/conf/`, or CLI
+  glue) so Hydra can import the new module.
 
 ### Introduce a reward function
 
@@ -195,9 +195,9 @@ Reference docs:
 
 ### Wire a new dataset
 
-- Mirror the layout in `areal/dataset/gsm8k.py`, `clevr_count_70k.py`, etc.: create
-  `areal/dataset/<name>.py` with `get_<name>_<type>_dataset` helpers for SFT/RL
-  variants.
+- Mirror the layout in `areal/dataset/gsm8k.py`, `geometry3k.py`, `clevr_count_70k.py`,
+  `hhrlhf.py`, or `torl_data.py`: create `areal/dataset/<name>.py` with
+  `get_<name>_<type>_dataset` helpers for SFT/RL variants.
 - Update `areal/dataset/__init__.py` by appending the dataset to `VALID_DATASETS` and
   adding a dispatch branch inside `_get_custom_dataset`.
 - Define the sample schema explicitly (`messages`, `answer`, `image_path`, metadata) and
@@ -217,7 +217,7 @@ Reference docs:
 - Read the example README to collect scheduler requirements, container images,
   environment variables, and any dataset preparation steps before running.
 - Keep rollout actors and inference engines version-aligned by propagating
-  `WeightUpdateMeta` (as shown in `examples/multi-turn-math/train.py`) and noting
+  `WeightUpdateMeta` (as shown in `examples/multi-turn-math/gsm8k_rl_mt.py`) and noting
   skipped weight updates explicitly if clusters are unavailable.
 - Capture the Hydra/CLI overrides you used
   (`python ... +train_dataset.path=... engine.type=...`) inside the PR/test plan so runs
@@ -261,8 +261,8 @@ Reference docs:
   (`is_in_ci`, `get_bool_env_var`). Prefer `pytest.fixture` + `pytest.mark.parametrize`
   over ad-hoc loops.
 - Keep tests hermetic by mocking engines/workflows similar to
-  `test_engine_api_workflow_resolution.py`; avoid spinning up real clusters unless you
-  are under `torchrun/` or `experimental/`.
+  `test_inference_engines.py`; avoid spinning up real clusters unless you are under
+  `torchrun/` or `experimental/`.
 - For GPU/distributed requirements, gate with `pytest.mark.skipif` or custom env checks
   (see `test_fsdp_engine_nccl.py` and `areal/tests/torchrun/`), and document the
   hardware dependency inside the skip reason.
@@ -277,7 +277,7 @@ Reference docs:
   command you would have executed.
 - **Workflow smoke tests**: `areal/tests/grpo` exercises rollout loops and expects CUDA;
   acknowledge when skipped.
-- **Distributed/FSDP suites**: `test_fsdp_*`, `test_sglang_engine.py`, RPC/torchrun
+- **Distributed/FSDP suites**: `test_fsdp_*`, `test_inference_engines.py`, RPC/torchrun
   folders require multi-node setups and distributed communication libraries. Call out
   the limitation explicitly.
 - **Static checks**: Pre-commit runs Ruff lint/format, mdformat, clang-format,
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
