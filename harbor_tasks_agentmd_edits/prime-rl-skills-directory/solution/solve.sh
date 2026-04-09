#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied (check for skills directory marker)
if [ -d "skills/inference-server" ] && [ -d "skills/toml-config" ] && grep -q "Skills live in" AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch for skills directory and AGENTS.md update
git apply - <<'PATCH'
diff --git a/.claude/skills b/.claude/skills
new file mode 120000
index 0000000000..42c5394a18
--- /dev/null
+++ b/.claude/skills
@@ -0,0 +1 @@
+../skills
\ No newline at end of file
diff --git a/AGENTS.md b/AGENTS.md
index ed1e88823f..c4cefbbcbb 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -41,8 +41,13 @@ Namespaces are one honking great idea -- let's do more of those!

 - Config files use `@` syntax: `uv run sft @ path/to/config.toml`
 - For multi-GPU with torchrun: `uv run torchrun --nproc-per-node 2 src/prime_rl/trainer/sft/train.py @ path/to/config.toml`
-- Boolean flags don't need `true`: use `--model.optim_cpu_offload` not `--model.optim_cpu_offload true`, use `--no-model.optim_cpu_offload` to pass False.
-- Override config values with CLI flags: `--model.name Qwen/Qwen3-0.6B --training.max_steps 100`
+- See the `toml-config` skill in `skills/` for full details on TOML structure, CLI overrides, and available commands.
+
+## Skills
+
+Skills live in `skills/` and are symlinked to `.claude/skills/`. They teach agents how to handle specific workflows (e.g. starting the inference server, writing configs). When you make changes to the codebase, check if any skills need to be updated to stay accurate.
+
+You are responsible for maintaining the skills folder. When a workflow fails and you fix it – whether with help from the user or through trial and error – you must update the skills to make implicit knowledge explicit. You are also responsible for keeping the skills up to date whenever you or anyone else modifies the code.

 ## Testing

diff --git a/skills/inference-server/SKILL.md b/skills/inference-server/SKILL.md
new file mode 100644
index 0000000000..bb6782d6fb
--- /dev/null
+++ b/skills/inference-server/SKILL.md
@@ -0,0 +1,49 @@
+---
+name: inference-server
+description: Start and test the prime-rl inference server. Use when asked to run inference, start vLLM, test a model, or launch the inference server.
+---
+
+# Inference Server
+
+## Starting the server
+
+Always use the `inference` entry point — never `vllm serve` or `python -m vllm.entrypoints.openai.api_server` directly. The entry point runs `setup_vllm_env()` which configures environment variables (LoRA, multiprocessing) before vLLM is imported.
+
+```bash
+# With a TOML config
+uv run inference @ path/to/config.toml
+
+# With CLI overrides
+uv run inference --model.name Qwen/Qwen3-0.6B --model.max_model_len 2048 --model.enforce_eager
+
+# Combined
+uv run inference @ path/to/config.toml --server.port 8001 --gpu-memory-utilization 0.5
+```
+
+## Custom endpoints
+
+The server extends vLLM with:
+
+- `/v1/chat/completions/tokens` — accepts token IDs as prompt input (used by multi-turn RL rollouts)
+- `/update_weights` — hot-reload model weights from the trainer
+- `/load_lora_adapter` — load LoRA adapters at runtime
+- `/init_broadcaster` — initialize weight broadcast for distributed training
+
+## Testing the server
+
+```bash
+curl http://localhost:8000/v1/chat/completions \
+  -H "Content-Type: application/json" \
+  -d '{
+    "model": "Qwen/Qwen3-0.6B",
+    "messages": [{"role": "user", "content": "Hi"}],
+    "max_tokens": 50
+  }'
+```
+
+## Key files
+
+- `src/prime_rl/inference/server.py` — entry point, env var setup
+- `src/prime_rl/inference/config.py` — `InferenceConfig` and all sub-configs
+- `src/prime_rl/inference/vllm/server.py` — FastAPI routes and vLLM monkey-patches
+- `configs/debug/infer.toml` — minimal debug config
diff --git a/skills/toml-config/SKILL.md b/skills/toml-config/SKILL.md
new file mode 100644
index 0000000000..ccbf127b10
--- /dev/null
+++ b/skills/toml-config/SKILL.md
@@ -0,0 +1,86 @@
+---
+name: toml-config
+description: How to write and use TOML configs in prime-rl. Use when creating config files, running commands with configs, or overriding config values via CLI.
+---
+
+# TOML Config
+
+All prime-rl commands use pydantic-settings with TOML configs and CLI overrides.
+
+## Running with configs
+
+```bash
+# Load a config file with @ syntax
+uv run inference @ configs/debug/infer.toml
+uv run sft @ configs/debug/sft/train.toml
+uv run rl @ configs/debug/rl/train.toml
+
+# CLI overrides (take precedence over TOML)
+uv run inference @ config.toml --model.name Qwen/Qwen3-0.6B --server.port 8001
+
+# Boolean flags: no value needed
+uv run inference --model.enforce_eager          # sets to true
+uv run inference --no-model.enforce_eager       # sets to false
+
+# CLI-only (no TOML file)
+uv run inference --model.name Qwen/Qwen3-0.6B --model.max_model_len 2048
+```
+
+## TOML structure
+
+Top-level fields must come before any `[section]` header — this is a TOML rule.
+
+```toml
+# Top-level fields first
gpu_memory_utilization = 0.5
+seed = 42
+
+# Then sections
+[model]
+name = "Qwen/Qwen3-0.6B"
+max_model_len = 4096
+
+[server]
+port = 8000
+```
+
+Putting a top-level field after a section header nests it inside that section, which causes validation errors.
+
+## Config inheritance
+
+Configs can inherit from other TOML files:
+
+```toml
+toml_files = ["base.toml"]
+
+[model]
+name = "Qwen/Qwen3-0.6B"  # overrides base
+```
+
+Paths in `toml_files` are relative to the file containing the field.
+
+## Setting None
+
+Use the string `"None"` in TOML to set a field to None:
+
+```toml
+max_model_len = "None"
+```
+
+## Available commands
+
+All accept `@ config.toml` and CLI overrides:
+
+| Command | Config class | Description |
+|---------|-------------|-------------|
+| `uv run rl` | full RL pipeline | Orchestrator + inference + trainer |
+| `uv run inference` | `InferenceConfig` | vLLM inference server |
+| `uv run trainer` | trainer config | RL trainer |
+| `uv run orchestrator` | orchestrator config | Rollout orchestrator |
+| `uv run env-server` | env server config | Environment server |
+| `uv run sft` | SFT config | Supervised fine-tuning |
+
+## Key files
+
+- `src/prime_rl/utils/pydantic_config.py` — `parse_argv`, `BaseSettings`, `@` syntax parsing
+- `configs/` — all config files, organized by task

PATCH

echo "Patch applied successfully."
