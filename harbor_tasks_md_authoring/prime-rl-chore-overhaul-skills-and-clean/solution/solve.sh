#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotency guard
if grep -qF "- **Minimal try/except**: let errors propagate \u2014 silent failures hide bugs. Only" "AGENTS.md" && grep -qF "- **Fail early**: incompatible option combinations (e.g. CP requires flash atten" "skills/config/SKILL.md" && grep -qF "description: All available prime-rl entrypoints \u2014 what they do, how to launch th" "skills/entrypoints/SKILL.md" && grep -qF "skills/inference-server/SKILL.md" "skills/inference-server/SKILL.md" && grep -qF "uv sync --all-extras # recommended: includes flash-attn, flash-attn-cute, etc." "skills/installation/SKILL.md" && grep -qF "- **Active task distribution**: check if tasks are distributed as expected acros" "skills/monitor-run/SKILL.md" && grep -qF "5. **Highlights**: group related PRs under a single highlight. Use `##` subsecti" "skills/release/SKILL.md" && grep -qF "skills/toml-config/SKILL.md" "skills/toml-config/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,15 +1,10 @@
 # AGENTS.md
 
-## Code Guidelines
-
-- Avoid try/except blocks unless it's really necessary.  It's fine that a program fails if something goes wrong as this helps us to catch non-obvious bugs and unforeseen side-effects earlier. You can add try catch on code that explicitly aims to be fault tolerant like adding retry mechanisms or explicit and intentional robustness. 
-
-- Do not add unnecessary comments. Especially do not try to explain code change that reflect your work process, do not refer to old code. "The code used to do that but now we are doing this" is not a pattern we want. Instead prefer to use targeted comments sparingly to explain ambiguous code.
-
-
-## Zen of Python
-remember the zen of python when writing code.
+## Writing code
 
+- **Minimal try/except**: let errors propagate — silent failures hide bugs. Only catch exceptions for intentional fault tolerance (retries, robustness).
+- **Targeted comments**: don't explain your work process or reference old code. Use targeted comments sparingly to clarify ambiguous logic.
+- **Zen of Python**: remember the Zen of Python when writing code.
 ```
 Beautiful is better than ugly.
 Explicit is better than implicit.
@@ -34,14 +29,8 @@ Namespaces are one honking great idea -- let's do more of those!
 
 ## Running code
 
-- All code should be runnable with `uv run` or `uv run <command>`.
-- All dependencies should already be installed and pin in the lock file. If not, add it to pyproject.toml and run `uv sync --all-extras` to install it.
-
-## CLI Usage
-
-- Config files use `@` syntax: `uv run sft @ path/to/config.toml`
-- For multi-GPU with torchrun: `uv run torchrun --nproc-per-node 2 src/prime_rl/trainer/sft/train.py @ path/to/config.toml`
-- See the `toml-config` skill in `skills/` for full details on TOML structure, CLI overrides, and available commands.
+- **Always use uv**: run code with `uv run` or `uv run <command>`, never raw `python`.
+- **Adding dependencies**: add to `pyproject.toml` and run `uv sync --all-extras` to install and lock them.
 
 ## Skills
 
@@ -55,18 +44,5 @@ Write tests as plain functions with pytest fixtures. Don't use class-based tests
 
 ## Git
 
-Branch prefixes: `feature/`, `fix/`, `chore/`
-
-## Releases
-
-When preparing release notes:
+Branch prefixes: `feat/`, `fix/`, `chore/`
 
-1. **Style reference**: check the previous release (`gh release list --limit 1` then `gh release view <tag>`) to match the tone and formatting.
-2. **Gather changes**: use `git log <last-tag>..origin/main --oneline --no-merges` to list all commits since the last release.
-2. **Check for new commits**: always `git fetch origin main` and re-check right before publishing, since PRs may have been merged while drafting.
-3. **Structure**: organize notes into numbered highlight sections (`# 1.`, `# 2.`, ...), then `# Breaking Changes`, `# Bug Fixes`, and `# Misc`.
-4. **Highlights**: group related PRs under a single highlight. Use `##` subsections when a highlight contains multiple items (e.g. Performance & Parallelism). Keep the top highlights for the most impactful user-facing features.
-5. **Config examples**: when referencing TOML config, verify the exact field names against the actual code or docs — don't guess.
-6. **Links**: use clickable links for docs (`[docs/foo.md](https://github.com/PrimeIntellect-ai/prime-rl/blob/main/docs/foo.md)`) and PR references (`[#1234](https://github.com/PrimeIntellect-ai/prime-rl/pull/1234)`).
-7. **Contributors**: list all contributors ranked by number of commits, using their GitHub `@username`. Get usernames via the GitHub API, not git author names (which can be inconsistent).
-8. **Draft first**: always create releases as `--draft` first, iterate on content, then publish.
diff --git a/skills/config/SKILL.md b/skills/config/SKILL.md
@@ -0,0 +1,176 @@
+---
+name: config
+description: How the prime-rl config system works — TOML files, CLI, config composition, and special patterns. Use when creating configs, debugging config errors, or overriding values via CLI.
+---
+
+# Config
+
+prime-rl uses `pydantic_config` (combines `tyro` and `pydantic`) for configuration. 
+
+## Use configs
+
+Every entrypoint accepts TOML files via `@` syntax and CLI overrides to configure it.
+
+```bash
+# Configure RL training with a TOML file
+uv run rl @ examples/reverse_text/rl.toml
+
+# Override specific fields via CLI
+uv run rl @ examples/reverse_text/rl.toml --max-steps 50
+```
+
+Config resolve in the following order:
+
+1. CLI arguments
+2. Config files (merged left-to-right)
+3. Class defaults (lowest)
+
+## Compose configs
+
+Multiple config files are merged left-to-right (later files override earlier ones):
+
+```bash
+uv run rl @ examples/reverse_text/rl.toml @ examples/reverse_text/slurm_rl.toml
+```
+
+Nested configs can be loaded for specific sections:
+
+```bash
+uv run rl --model @ model.toml --data @ data.toml
+```
+
+Mixed composition works too:
+
+```bash
+uv run rl @ base.toml --trainer @ trainer_override.toml --trainer.lr 1e-3
+```
+
+Merging is deep — unset fields in the override are preserved from the base config.
+
+## Inspect & validate configs
+
+Use `--help` to see all available fields and their defaults. When combined with a config file, defaults reflect the TOML values:
+
+```bash
+uv run rl --help                                  # shows class defaults
+uv run rl @ examples/reverse_text/rl.toml --help  # shows defaults from TOML
+```
+
+Use `--dry-run` to validate and dump the fully resolved config:
+
+```bash
+uv run rl @ examples/reverse_text/rl.toml --dry-run --output-dir /tmp/test
+# Writes resolved TOML to /tmp/test/configs
+```
+
+## Naming
+
+CLI uses kebab-case (`--model.max-model-len`), TOML uses snake_case (`max_model_len`). Both refer to the same field.
+
+## General rules
+
+- **Fail early**: incompatible option combinations (e.g. CP requires flash attention, NCCL broadcast requires async level 1) should raise in `model_validator` at config resolution time, not at runtime. When adding new constraints, add a validator to the config class.
+- **Deprecation**: when renaming or removing config fields, emit a deprecation warning with a clear migration path (e.g. "field X is deprecated, use Y instead"). Do not silently drop fields — help users update their configs.
+
+## Important patterns
+
+### Boolean fields
+
+```bash
+uv run inference --model.enforce-eager          # sets to true
+uv run inference --model.no-enforce-eager       # sets to false
+```
+
+In TOML, booleans must be explicit:
+
+```toml
+[model]
+enforce_eager = true
+```
+
+### None fields
+
+TOML has no null type. Use the string `"None"`:
+
+```toml
+max_model_len = "None"
+```
+
+On the CLI, pass `None` as a plain string:
+
+```bash
+uv run inference --model.max-model-len None
+```
+
+### List fields
+
+In TOML, use `[[double brackets]]` (array of tables) for lists of objects:
+
+```toml
+[[orchestrator.env]]
+id = "reverse-text"
+
+[[orchestrator.env]]
+id = "math-env"
+```
+
+On the CLI, list items are indexed: `--env.0.id reverse-text --env.1.id math-env`.
+
+### Dict fields
+
+In TOML, use a section:
+
+```toml
+[vllm_extra]
+key1 = "value1"
+key2 = 123
+```
+
+On the CLI, pass as a JSON string:
+
+```bash
+uv run inference --vllm-extra '{"key1": "value1", "key2": 123}'
+```
+
+### Discriminated unions
+
+Some config fields use discriminated unions (e.g. loss type, data type). Set the `type` field to select the variant:
+
+```toml
+[trainer.loss]
+type = "sft"
+
+[data]
+type = "fake"
+batch_size = 2
+```
+
+On the CLI:
+
+```bash
+uv run sft --data.type fake --data.batch-size 4
+```
+
+If you wish to configure values of the default variant, you don't need to set the `type` field.
+
+### Model fields
+
+For `BaseModel | None` fields (like `[ckpt]`, `[wandb]`, `[compile]`), a bare flag enables them with defaults:
+
+```bash
+uv run rl @ config.toml --model.compile              # enables compilation with defaults (fullgraph = false)
+uv run rl @ config.toml --model.compile.fullgraph    # enables compilation and sets nested field (fullgraph = true)
+```
+
+In TOML, an empty section header does the same:
+
+```toml
+[ckpt]  # enables checkpointing with defaults
+```
+
+## Key files
+
+- `src/prime_rl/utils/config.py` — re-exports `BaseConfig` and `cli` from pydantic_config
+- `src/prime_rl/configs/` — all domain-specific config classes
+- `configs/debug/` — minimal debug configs for testing
+- `examples/` — full example configs for various tasks
diff --git a/skills/entrypoints/SKILL.md b/skills/entrypoints/SKILL.md
@@ -0,0 +1,91 @@
+---
+name: entrypoints
+description: All available prime-rl entrypoints — what they do, how to launch them, and which config class they use. Use when running commands, launching training, or starting servers.
+---
+
+# Entrypoints
+
+All entrypoints are run via `uv run <command>` and accept TOML configs via `@ path/to/config.toml` with CLI overrides. See the `config` skill for config system details.
+
+## `rl` — RL training
+
+Orchestrates the complete RL loop: launches inference server, orchestrator, and trainer as subprocesses.
+
+```bash
+uv run rl @ examples/reverse_text/rl.toml
+uv run rl @ examples/reverse_text/rl.toml @ examples/reverse_text/slurm_rl.toml # with SLURM
+uv run rl @ examples/reverse_text/rl.toml --dry-run # generate scripts without running
+```
+
+- **Config:** `RLConfig` (`src/prime_rl/configs/rl.py`)
+- **Entrypoint:** `src/prime_rl/entrypoints/rl.py`
+- **SLURM:** yes — single-node and multi-node
+
+## `sft` — SFT training
+
+Trains a model on labeled data. Uses torchrun for distributed training.
+
+```bash
+uv run sft @ examples/reverse_text/sft.toml
+uv run sft @ examples/reverse_text/sft.toml --slurm # with SLURM
+uv run sft @ examples/reverse_text/sft.toml --dry-run # generate scripts without running
+```
+
+The entrypoint launches torchrun internally — no need to call torchrun directly.
+
+- **Config:** `SFTConfig` (`src/prime_rl/configs/sft.py`)
+- **Entrypoint:** `src/prime_rl/entrypoints/sft.py`
+- **SLURM:** yes — single-node and multi-node
+
+## `inference` — Standalone inference server
+
+Launches a vLLM-based inference server with OpenAI-compatible API.
+
+```bash
+uv run inference @ configs/debug/infer.toml
+uv run inference --model.name Qwen/Qwen3-0.6B --model.enforce-eager
+```
+
+Always use the `inference` entrypoint — never `vllm serve` directly.
+
+Custom endpoints beyond standard OpenAI API:
+- `/v1/chat/completions/tokens` — accepts token IDs as prompt input
+- `/update_weights` — hot-reload model weights from the trainer
+- `/load_lora_adapter` — load LoRA adapters at runtime
+- `/init_broadcaster` — initialize weight broadcast for distributed training
+
+Check health with:
+```bash
+curl http://<ip>:<port>/health
+```
+
+Check served models with:
+```bash
+curl http://<ip>:<port>/v1/models
+```
+
+Test chat completions with:
+```bash
+curl http://localhost:8000/v1/chat/completions \
+  -H "Content-Type: application/json" \
+  -d '{"model": "Qwen/Qwen3-0.6B", "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 50}'
+```
+
+- **Config:** `InferenceConfig` (`src/prime_rl/configs/inference.py`)
+- **Entrypoint:** `src/prime_rl/entrypoints/inference.py`
+- **SLURM:** yes — single-node, multi-node, and disaggregated deployments
+
+## Summary
+
+| Command | Purpose | SLURM | Typical use |
+|---------|---------|-------|-------------|
+| `rl` | Full RL pipeline | yes | Production RL training |
+| `sft` | Supervised fine-tuning | yes | SFT training |
+| `inference` | vLLM server | yes | Standalone inference or debugging |
+
+## Key directories
+
+- `src/prime_rl/entrypoints/` — top-level entrypoints (`rl`, `sft`, `inference`)
+- `src/prime_rl/configs/` — all config classes
+- `configs/debug/` — minimal configs for quick testing
+- `examples/` — full example configs for various tasks
diff --git a/skills/inference-server/SKILL.md b/skills/inference-server/SKILL.md
@@ -1,109 +0,0 @@
----
-name: inference-server
-description: Start and test the prime-rl inference server. Use when asked to run inference, start vLLM, test a model, or launch the inference server.
----
-
-# Inference Server
-
-## Starting the server
-
-Always use the `inference` entry point — never `vllm serve` or `python -m vllm.entrypoints.openai.api_server` directly. The entry point runs `setup_vllm_env()` which configures environment variables (LoRA, multiprocessing) before vLLM is imported.
-
-```bash
-# With a TOML config
-uv run inference @ path/to/config.toml
-
-# With CLI overrides
-uv run inference --model.name Qwen/Qwen3-0.6B --model.max_model_len 2048 --model.enforce_eager
-
-# Combined
-uv run inference @ path/to/config.toml --server.port 8001 --gpu-memory-utilization 0.5
-```
-
-## SLURM scheduling
-
-The inference entrypoint supports optional SLURM scheduling, following the same patterns as SFT and RL.
-
-### Single-node SLURM
-
-```toml
-# inference_slurm.toml
-output_dir = "/shared/outputs/my-inference"
-
-[model]
-name = "Qwen/Qwen3-8B"
-
-[parallel]
-tp = 8
-
-[slurm]
-job_name = "my-inference"
-partition = "cluster"
-```
-
-```bash
-uv run inference @ inference_slurm.toml
-```
-
-### Multi-node SLURM (independent vLLM replicas)
-
-Each node runs an independent vLLM instance. No cross-node parallelism — TP and DP must fit within a single node's GPUs.
-
-```toml
-# inference_multinode.toml
-output_dir = "/shared/outputs/my-inference"
-
-[model]
-name = "PrimeIntellect/INTELLECT-3-RL-600"
-
-[parallel]
-tp = 8
-dp = 1
-
-[deployment]
-type = "multi_node"
-num_nodes = 4
-gpus_per_node = 8
-
-[slurm]
-job_name = "my-inference"
-partition = "cluster"
-```
-
-### Dry run
-
-Add `dry_run = true` to generate the sbatch script without submitting:
-
-```bash
-uv run inference @ config.toml --dry-run true
-```
-
-## Custom endpoints
-
-The server extends vLLM with:
-
-- `/v1/chat/completions/tokens` — accepts token IDs as prompt input (used by multi-turn RL rollouts)
-- `/update_weights` — hot-reload model weights from the trainer
-- `/load_lora_adapter` — load LoRA adapters at runtime
-- `/init_broadcaster` — initialize weight broadcast for distributed training
-
-## Testing the server
-
-```bash
-curl http://localhost:8000/v1/chat/completions \
-  -H "Content-Type: application/json" \
-  -d '{
-    "model": "Qwen/Qwen3-0.6B",
-    "messages": [{"role": "user", "content": "Hi"}],
-    "max_tokens": 50
-  }'
-```
-
-## Key files
-
-- `src/prime_rl/entrypoints/inference.py` — entrypoint with local/SLURM routing
-- `src/prime_rl/inference/server.py` — vLLM env setup
-- `src/prime_rl/configs/inference.py` — `InferenceConfig` and all sub-configs
-- `src/prime_rl/inference/vllm/server.py` — FastAPI routes and vLLM monkey-patches
-- `src/prime_rl/templates/inference.sbatch.j2` — SLURM template (handles both single and multi-node)
-- `configs/debug/infer.toml` — minimal debug config
diff --git a/skills/installation/SKILL.md b/skills/installation/SKILL.md
@@ -5,25 +5,16 @@ description: How to install prime-rl and its optional dependencies. Use when set
 
 # Installation
 
-## Basic install
-
-```bash
-uv sync
-```
-
-This installs all core dependencies defined in `pyproject.toml`.
-
-## All extras at once
-
-The recommended way to install for most users:
-
+## Basic
 ```bash
-uv sync --all-extras
+uv sync              # core dependencies only
+uv sync --group dev  # dev tools: pytest, ruff, pre-commit
+uv sync --all-extras # recommended: includes flash-attn, flash-attn-cute, etc.
 ```
 
-This installs all optional extras (flash-attn, flash-attn-cute, etc.) in one go.
+## Advanced
 
-## Mamba-SSM (NemotronH models)
+### Mamba-SSM (NemotronH models)
 
 For NemotronH (hybrid Mamba-Transformer-MoE) models, install `mamba-ssm` for Triton-based SSD kernels that match vLLM's precision:
 
@@ -35,7 +26,7 @@ Requires `nvcc` (CUDA toolkit). Without `mamba-ssm`, NemotronH falls back to HF'
 
 Note: do NOT install `causal-conv1d` unless your GPU architecture matches the compiled CUDA kernels. The code automatically falls back to PyTorch nn.Conv1d when it's absent.
 
-## FP8 inference with deep-gemm
+### FP8 inference with deep-gemm
 
 For certain models like GLM-5-FP8, you need `deep-gemm`. Install it via the `fp8-inference` dependency group:
 
@@ -45,14 +36,6 @@ uv sync --group fp8-inference
 
 This installs the pre-built `deep-gemm` wheel. No CUDA build step is needed.
 
-## Dev dependencies
-
-```bash
-uv sync --group dev
-```
-
-Installs pytest, ruff, pre-commit, and other development tools.
-
 ## Key files
 
 - `pyproject.toml` — all dependencies, extras, and dependency groups
diff --git a/skills/monitor-run/SKILL.md b/skills/monitor-run/SKILL.md
@@ -0,0 +1,120 @@
+---
+name: monitor-run
+description: How to monitor ongoing training runs — find output directories, check logs, diagnose performance, and inspect SLURM jobs. Use when asked to check on a run, debug training issues, or investigate performance.
+---
+
+# Monitor a Run
+
+## Find the output directory
+
+The output directory is set in the config (`output_dir`). To find it:
+
+- **Local run**: check the resolved config at `{output_dir}/configs/rl.toml` or `sft.toml`
+- **SLURM run**: check `squeue -u $USER` to find the job, then look at the sbatch script or the config dir
+
+## RL
+
+### Check GPU allocation
+
+#### Single-node
+
+GPUs are assigned in order: inference first, then trainer, then teacher (if any).
+
+```
+GPU 0..N-1     → inference (vLLM)
+GPU N..M-1     → trainer (torchrun)
+GPU M..K-1     → teacher inference (optional)
+```
+
+The exact split is controlled by `deployment.num_infer_gpus`, `deployment.num_train_gpus`, and `deployment.num_teacher_gpus`. The orchestrator runs as a separate process (no GPU). Check the resolved config at `{output_dir}/configs/rl.toml` for the actual values.
+
+#### Multi-node (SLURM)
+
+```bash
+squeue -u $USER -o "%.18i %.9P %.30j %.8T %.10M %.6D %R"
+```
+
+Nodes from the SLURM allocation are split in order: inference nodes first, then trainer nodes.
+
+```
+Nodes 0..I-1   → inference (vLLM, first node of each replica also runs vllm-router)
+Nodes I..I+T-1 → trainer (torchrun, rank 0 node also runs the orchestrator)
+```
+
+The node assignment is visible in the generated sbatch script at `{output_dir}/rl.sbatch` and in the SLURM logs under `{output_dir}/slurm/`.
+
+### Check logs
+
+#### Local runs
+
+```
+{output_dir}/logs/
+├── rl.log                    # main launcher log
+├── inference.stdout          # vLLM inference server
+├── orchestrator.stdout       # orchestrator process
+├── trainer.stdout            # torchrun wrapper output
+├── trainer/
+│   ├── rank_0.log            # per-rank trainer logs (rank 0 is most useful)
+│   └── ...
+└── envs/
+    ├── train/{env_name}/
+    │   ├── env_server.log
+    │   └── env_worker_{id}.log
+    └── eval/{env_name}/
+        └── ...
+```
+
+#### SLURM runs
+
+```
+{output_dir}/slurm/
+├── latest_train_node_rank_{N}.log        # trainer nodes
+├── latest_orchestrator.log               # orchestrator
+├── latest_infer_node_rank_{N}.log        # inference nodes
+├── latest_router_replica_{N}.log         # vllm-router (if multi-node inference)
+└── job_{SLURM_JOB_ID}_*.log              # permanent copies
+```
+
+Env server logs are still under `{output_dir}/logs/envs/`.
+
+### Check performance
+
+#### Trainer
+
+Check `{output_dir}/logs/trainer/rank_0.log` or the SLURM trainer log.
+
+Key metrics per step:
+- `time/step` — total step time
+- `time/wait_for_batch` — time waiting for the orchestrator to deliver a batch
+- `time/forward_backward` — forward/backward pass time
+- `time/broadcast_weights` — time broadcasting weights to inference servers
+- `time/save_ckpt` — checkpoint save time
+
+High `wait_for_batch` means the orchestrator is the bottleneck (slow rollouts, slow envs, or too few inference replicas).
+
+#### Orchestrator
+
+Check `{output_dir}/logs/orchestrator.log` or the SLURM orchestrator log.
+
+Key metrics per step:
+- `time/step` — total orchestrator step time
+- `time/generate_completions` — rollout generation time
+- `time/wait_for_ckpt` — time waiting for trainer checkpoint
+- `time/update_weights` — weight update time
+- `scheduler/async_level` — current async level
+- `empty_rollouts/all` — fraction of empty rollouts
+- `errored_rollouts/all` — fraction of errored rollouts
+
+High `wait_for_ckpt` means the trainer is the bottleneck. The orchestrator logs when it pauses/resumes:
+```
+"Orchestrator paused: waiting for trainer process to complete checkpoint ..."
+"Orchestrator resumed: checkpoint ... ready (after ...s)"
+```
+
+#### Env servers
+
+Check `{output_dir}/logs/envs/train/{env_name}/env_server.log` and `{output_dir}/logs/envs/train/{env_name}/env_worker_{id}.log`.
+
+Key things to look for:
+- **Event loop lag**: server logs aggregate lag stats (min/mean/median/p90/p99/max) of itself and all workers periodically. check that neither is overloaded
+- **Active task distribution**: check if tasks are distributed as expected across workers per-env and across envs. uneven distribution suggests some workers/envs are slower. heavily skewed distribution can indicate that a env is bottlenecking the trainer or has stopped being responsive.
\ No newline at end of file
diff --git a/skills/release/SKILL.md b/skills/release/SKILL.md
@@ -0,0 +1,18 @@
+---
+name: release
+description: How to prepare and publish GitHub releases for prime-rl. Use when drafting release notes, tagging versions, or publishing releases.
+---
+
+# Releases
+
+## Preparing release notes
+
+1. **Style reference**: check the previous release (`gh release list --limit 1` then `gh release view <tag>`) to match the tone and formatting.
+2. **Gather changes**: use `git log <last-tag>..origin/main --oneline --no-merges` to list all commits since the last release.
+3. **Check for new commits**: always `git fetch origin main` and re-check right before publishing, since PRs may have been merged while drafting.
+4. **Structure**: organize notes into numbered highlight sections (`# 1.`, `# 2.`, ...), then `# Breaking Changes`, `# Bug Fixes`, and `# Misc`.
+5. **Highlights**: group related PRs under a single highlight. Use `##` subsections when a highlight contains multiple items (e.g. Performance & Parallelism). Keep the top highlights for the most impactful user-facing features.
+6. **Config examples**: when referencing TOML config, verify the exact field names against the actual code or docs — don't guess.
+7. **Links**: use clickable links for docs (`[docs/foo.md](https://github.com/PrimeIntellect-ai/prime-rl/blob/main/docs/foo.md)`) and PR references (`[#1234](https://github.com/PrimeIntellect-ai/prime-rl/pull/1234)`).
+8. **Contributors**: list all contributors ranked by number of commits, using their GitHub `@username`. Get usernames via the GitHub API, not git author names (which can be inconsistent).
+9. **Draft first**: always create releases as `--draft` first, iterate on content, then publish.
diff --git a/skills/toml-config/SKILL.md b/skills/toml-config/SKILL.md
@@ -1,165 +0,0 @@
----
-name: toml-config
-description: How to write and use TOML configs in prime-rl. Use when creating config files, running commands with configs, or overriding config values via CLI.
----
-
-# TOML Config
-
-All prime-rl commands use `pydantic_config` (tyro-backed) with TOML configs and CLI overrides.
-
-## Running with configs
-
-```bash
-# Load a config file with @ syntax
-uv run inference @ configs/debug/infer.toml
-uv run sft @ configs/debug/sft/train.toml
-uv run rl @ configs/debug/rl/train.toml
-
-# CLI overrides (take precedence over TOML)
-uv run inference @ config.toml --model.name Qwen/Qwen3-0.6B --server.port 8001
-
-# Boolean flags: no value needed
-uv run inference --model.enforce-eager          # sets to true
-uv run inference --no-model.enforce-eager       # sets to false
-
-# CLI-only (no TOML file)
-uv run inference --model.name Qwen/Qwen3-0.6B --model.max-model-len 2048
-
-# Compose multiple config files (later files override earlier ones)
-uv run rl @ examples/reverse_text/rl.toml @ examples/reverse_text/slurm_rl.toml
-
-# Nested config files: load a config for a specific section
-uv run rl --model @ model.toml --data @ data.toml
-```
-
-## TOML structure
-
-Top-level fields must come before any `[section]` header — this is a TOML rule.
-
-```toml
-# Top-level fields first
-gpu_memory_utilization = 0.5
-seed = 42
-
-# Then sections
-[model]
-name = "Qwen/Qwen3-0.6B"
-max_model_len = 4096
-
-[server]
-port = 8000
-```
-
-Putting a top-level field after a section header nests it inside that section, which causes validation errors.
-
-## Setting None
-
-Use the string `"None"` in TOML to set a field to None:
-
-```toml
-max_model_len = "None"
-```
-
-## SLURM mode
-
-Both `rl` and `sft` commands support SLURM execution via an optional `[slurm]` section. When present, the run is submitted as a SLURM job instead of running locally.
-
-SLURM configs are composed with the base config via CLI:
-```bash
-uv run rl @ examples/reverse_text/rl.toml @ examples/reverse_text/slurm_rl.toml
-```
-
-### RL SLURM
-
-```toml
-output_dir = "/shared/experiments/my-run"
-
-[deployment]
-type = "multi_node"
-num_train_nodes = 2
-num_infer_nodes = 1
-gpus_per_node = 8
-# nodes_per_fsdp_group = 1
-
-[slurm]
-job_name = "my-rl-job"
-# dry_run = true          # generate script without submitting
-# template_path = "path/to/custom.sh.j2"
-# project_dir = "/path/to/project"
-```
-
-When `[slurm]` is set for RL:
-- `output_dir` must be explicitly set (the default `outputs` is rejected)
-- Teacher inference is not supported in multi-node deployment
-
-### SFT SLURM
-
-```toml
-output_dir = "/shared/experiments/my-sft-run"
-
-[deployment]
-type = "multi_node"
-num_nodes = 2
-gpus_per_node = 8
-# nodes_per_fsdp_group = 1
-
-[slurm]
-job_name = "my-sft-job"
-# dry_run = true
-# template_path = "path/to/custom.sh.j2"
-# project_dir = "/path/to/project"
-```
-
-SFT deployment follows the same pattern as RL:
-- `[deployment]` configures node/GPU allocation (`single_node` default or `multi_node`)
-- `[slurm]` configures SLURM submission (job name, partition, template)
-- `output_dir` must be explicitly set when using SLURM
-- Multi-node deployment requires `[slurm]` to be set
-
-## SFT Distillation (Hard Distillation) With Teacher Rollouts
-
-Use this when the teacher is an external OpenAI-compatible endpoint and you want to train from teacher completions directly (no teacher token logprobs required).
-
-```toml
-[trainer.loss]
-type = "sft"
-
-[orchestrator]
-use_token_client = false
-
-[orchestrator.teacher_rollout_model.client]
-base_url = ["https://your-openai-compatible-endpoint/v1"]
-skip_model_check = true
-
-[orchestrator.teacher_rollout_model.model]
-name = "teacher-model-name"
-```
-
-Notes:
-- `orchestrator.teacher_rollout_model` switches rollout generation to the external teacher endpoint.
-- `use_token_client = false` is required when `orchestrator.teacher_rollout_model` is set.
-- `trainer.loss.type = "sft"` makes the RL trainer optimize masked NLL like SFT.
-- In this mode, omit `[inference]`.
-- Image input is supported when using a VLM student model and OpenAI-style image messages (`data:image/...`).
-
-## Available commands
-
-All accept `@ config.toml` and CLI overrides:
-
-| Command | Config class | Description |
-|---------|-------------|-------------|
-| `uv run rl` | full RL pipeline | Orchestrator + inference + trainer (local or SLURM) |
-| `uv run inference` | `InferenceConfig` | vLLM inference server |
-| `uv run trainer` | trainer config | RL trainer |
-| `uv run orchestrator` | orchestrator config | Rollout orchestrator |
-| `uv run env-server` | env server config | Environment server |
-| `uv run sft` | SFT config | Supervised fine-tuning (local or SLURM) |
-
-## Key files
-
-- `src/prime_rl/utils/config.py` — `BaseConfig`, `cli`, `get_all_fields`
-- `src/prime_rl/entrypoints/rl.py` — unified RL entrypoint (local + SLURM)
-- `src/prime_rl/configs/rl.py` — `RLConfig`, `SlurmConfig, DeploymentConfig`
-- `src/prime_rl/entrypoints/sft.py` — unified SFT entrypoint (local + SLURM)
-- `src/prime_rl/configs/sft.py` — `SFTConfig`
-- `configs/` — all config files, organized by task
PATCH

echo "Gold patch applied."
