# Agent Config Files for prime-rl-toml-none-str-removal

Repo: PrimeIntellect-ai/prime-rl
Commit: 4f612601f6447b3df1ee17e535ac698b5cc3d16c
Files found: 6


---
## AGENTS.md

```
   1 | # AGENTS.md
   2 | 
   3 | ## Code Guidelines
   4 | 
   5 | - Avoid try/except blocks unless it's really necessary.  It's fine that a program fails if something goes wrong as this helps us to catch non-obvious bugs and unforeseen side-effects earlier. You can add try catch on code that explicitly aims to be fault tolerant like adding retry mechanisms or explicit and intentional robustness. 
   6 | 
   7 | - Do not add unnecessary comments. Especially do not try to explain code change that reflect your work process, do not refer to old code. "The code used to do that but now we are doing this" is not a pattern we want. Instead prefer to use targeted comments sparingly to explain ambiguous code.
   8 | 
   9 | 
  10 | ## Zen of Python
  11 | remember the zen of python when writing code.
  12 | 
  13 | ```
  14 | Beautiful is better than ugly.
  15 | Explicit is better than implicit.
  16 | Simple is better than complex.
  17 | Complex is better than complicated.
  18 | Flat is better than nested.
  19 | Sparse is better than dense.
  20 | Readability counts.
  21 | Special cases aren't special enough to break the rules.
  22 | Although practicality beats purity.
  23 | Errors should never pass silently.
  24 | Unless explicitly silenced.
  25 | In the face of ambiguity, refuse the temptation to guess.
  26 | There should be one-- and preferably only one --obvious way to do it.
  27 | Although that way may not be obvious at first unless you're Dutch.
  28 | Now is better than never.
  29 | Although never is often better than *right* now.
  30 | If the implementation is hard to explain, it's a bad idea.
  31 | If the implementation is easy to explain, it may be a good idea.
  32 | Namespaces are one honking great idea -- let's do more of those!
  33 | ```
  34 | 
  35 | ## Running code
  36 | 
  37 | - All code should be runnable with `uv run` or `uv run <command>`.
  38 | - All dependencies should already be installed and pin in the lock file. If not, add it to pyproject.toml and run `uv sync --all-extras` to install it.
  39 | 
  40 | ## CLI Usage
  41 | 
  42 | - Config files use `@` syntax: `uv run sft @ path/to/config.toml`
  43 | - For multi-GPU with torchrun: `uv run torchrun --nproc-per-node 2 src/prime_rl/trainer/sft/train.py @ path/to/config.toml`
  44 | - See the `toml-config` skill in `skills/` for full details on TOML structure, CLI overrides, and available commands.
  45 | 
  46 | ## Skills
  47 | 
  48 | Skills live in `skills/` and are symlinked to `.claude/skills/`. They teach agents how to handle specific workflows (e.g. starting the inference server, writing configs). When you make changes to the codebase, check if any skills need to be updated to stay accurate.
  49 | 
  50 | You are responsible for maintaining the skills folder. When a workflow fails and you fix it – whether with help from the user or through trial and error – you must update the skills to make implicit knowledge explicit. You are also responsible for keeping the skills up to date whenever you or anyone else modifies the code.
  51 | 
  52 | ## Testing
  53 | 
  54 | Write tests as plain functions with pytest fixtures. Don't use class-based tests.
  55 | 
  56 | ## Git
  57 | 
  58 | Branch prefixes: `feature/`, `fix/`, `chore/`
  59 | 
  60 | ## Releases
  61 | 
  62 | When preparing release notes:
  63 | 
  64 | 1. **Style reference**: check the previous release (`gh release list --limit 1` then `gh release view <tag>`) to match the tone and formatting.
  65 | 2. **Gather changes**: use `git log <last-tag>..origin/main --oneline --no-merges` to list all commits since the last release.
  66 | 2. **Check for new commits**: always `git fetch origin main` and re-check right before publishing, since PRs may have been merged while drafting.
  67 | 3. **Structure**: organize notes into numbered highlight sections (`# 1.`, `# 2.`, ...), then `# Breaking Changes`, `# Bug Fixes`, and `# Misc`.
  68 | 4. **Highlights**: group related PRs under a single highlight. Use `##` subsections when a highlight contains multiple items (e.g. Performance & Parallelism). Keep the top highlights for the most impactful user-facing features.
  69 | 5. **Config examples**: when referencing TOML config, verify the exact field names against the actual code or docs — don't guess.
  70 | 6. **Links**: use clickable links for docs (`[docs/foo.md](https://github.com/PrimeIntellect-ai/prime-rl/blob/main/docs/foo.md)`) and PR references (`[#1234](https://github.com/PrimeIntellect-ai/prime-rl/pull/1234)`).
  71 | 7. **Contributors**: list all contributors ranked by number of commits, using their GitHub `@username`. Get usernames via the GitHub API, not git author names (which can be inconsistent).
  72 | 8. **Draft first**: always create releases as `--draft` first, iterate on content, then publish.
```


---
## CLAUDE.md

```
   1 | @AGENTS.md
```


---
## README.md

```
   1 | <p align="center">
   2 | </p>
   3 | 
   4 | <p align="center">
   5 |   <img src="https://github.com/user-attachments/assets/40c36e38-c5bd-4c5a-9cb3-f7b902cd155d#gh-light-mode-only" alt="Prime Intellect" width="312">
   6 |   <img src="https://github.com/user-attachments/assets/6414bc9b-126b-41ca-9307-9e982430cde8#gh-dark-mode-only"  alt="Prime Intellect" width="312">
   7 | </p>
   8 | 
   9 | ---
  10 | 
  11 | <h3 align="center">
  12 | PRIME-RL: Async RL Training at Scale
  13 | </h3>
  14 | 
  15 | ---
  16 | 
  17 | </br>
  18 | <p align="center">
  19 |   <a href="https://github.com/PrimeIntellect-ai/prime-rl/actions/workflows/style.yaml">
  20 |     <img src="https://github.com/PrimeIntellect-ai/prime-rl/actions/workflows/style.yaml/badge.svg" alt="Style" />
  21 |   </a>
  22 |   <a href="https://github.com/PrimeIntellect-ai/prime-rl/actions/workflows/cpu_tests.yaml">
  23 |     <img src="https://github.com/PrimeIntellect-ai/prime-rl/actions/workflows/cpu_tests.yaml/badge.svg" alt="Test" />
  24 |   </a>
  25 |   <a href="https://github.com/PrimeIntellect-ai/prime-rl/actions/workflows/gpu_tests.yaml">
  26 |     <img src="https://github.com/PrimeIntellect-ai/prime-rl/actions/workflows/gpu_tests.yaml/badge.svg" alt="Test" />
  27 |   </a>
  28 | </p>
  29 | 
  30 | ## Overview
  31 | 
  32 | PRIME-RL is a framework for large-scale asynchronous reinforcement learning. It is designed to be easy-to-use and hackable, yet capable of scaling to 1000+ GPUs. Beyond that, here is why we think you might like it:
  33 | 
  34 | 1. Integrates natively with [`verifiers`](https://github.com/PrimeIntellect-ai/verifiers) environments via the [Environments Hub](https://app.primeintellect.ai/dashboard/environments?ex_sort=most_stars)
  35 | 2. Supports end-to-end post-training, including SFT and RL training and evals
  36 | 3. Multi-node deployment with [FSDP2](https://docs.pytorch.org/tutorials/intermediate/FSDP_tutorial.html) training and [vLLM](https://github.com/vllm-project/vllm) inference backend
  37 | 4. Designed for asynchronous agentic RL training at scale
  38 | 5. Hackable, modular and extensible by nature
  39 | 
  40 | ## Setup
  41 | 
  42 | > *We develop and test on NVIDIA RTX 3090/4090/5090, A100, H100, H200, and B200. If your setup fails, please create an [issue](https://github.com/PrimeIntellect-ai/prime-rl/issues).*
  43 | 
  44 | ### Prerequisites
  45 | 
  46 | Currently, you **need at least one NVIDIA GPU to use PRIME-RL**. If you don't already have access to one, we recommend our [compute platform](https://app.primeintellect.ai) for everything from renting on-demand single GPUs for developing, debugging and small ablations, to [reserving 1000+ GPU clusters](https://app.primeintellect.ai/dashboard/quotes) for production-scale training.
  47 | 
  48 | ### Quick Setup
  49 | 
  50 | Set up PRIME-RL in a single command.
  51 | 
  52 | ```bash
  53 | curl -sSL https://raw.githubusercontent.com/PrimeIntellect-ai/prime-rl/main/scripts/install.sh | bash
  54 | ```
  55 | 
  56 | <details>
  57 | <summary>
  58 | Manual Setup
  59 | </summary>
  60 | <br>
  61 | 
  62 | 1. Clone the repository
  63 | 
  64 | ```bash
  65 | git clone https://github.com/PrimeIntellect-ai/prime-rl.git
  66 | cd prime-rl
  67 | ```
  68 | 
  69 | 2. Install [uv](https://docs.astral.sh/uv/)
  70 | 
  71 | ```bash
  72 | curl -LsSf https://astral.sh/uv/install.sh | sh
  73 | source $HOME/.local/bin/env
  74 | ```
  75 | 
  76 | 3. Install dependencies from the lock file
  77 | 
  78 | ```bash
  79 | uv sync --all-extras
  80 | ```
  81 | 
  82 | 3.1. Optional: Install Flash Attention 3 (on Hopper GPUs only, for flash_attention_3 attention backend)
  83 | 
  84 | > *NOTE*: This step will take a while, as it builds the Flash Attention 3 extension from source, as it has no wheels prebuilt.
  85 | > *NOTE*: After this step, you can't run `uv sync --all-extras` or `uv run` as it will uninstall the package, you can avoid it by running `uv sync --inexact` or `uv run --no-sync`
  86 | 
  87 | ```bash
  88 | uv pip install "flash-attn-3 @ git+https://github.com/Dao-AILab/flash-attention.git@main#subdirectory=hopper" --no-build-isolation
  89 | ```
  90 | 
  91 | </details>
  92 | 
  93 | <details>
  94 | <summary>
  95 | Validate your environment setup
  96 | </summary>
  97 | <br>
  98 | 
  99 | 1. Check that the environment uses Python 3.12
 100 | 
 101 | ```bash
 102 | uv run python -V
 103 | ```
 104 | 
 105 | 2. Check that `flash-attn` is installed
 106 | 
 107 | ```bash
 108 | uv run python -c "import flash_attn"
 109 | ```
 110 | 
 111 | 3. Check that you can run SFT trainer  (*this requires 1 GPU*)
 112 | 
 113 | ```bash
 114 | uv run sft @ configs/debug/sft/train.toml
 115 | ```
 116 | 
 117 | 4. Check that you can run the RL trainer (*this requires 1 GPU*)
 118 | 
 119 | ```bash
 120 | uv run trainer @ configs/debug/rl/train.toml
 121 | ```
 122 | 
 123 | 5. Check that you can run the inference server (*this requires 1 GPU*)
 124 | 
 125 | ```bash
 126 | uv run inference @ configs/debug/infer.toml
 127 | ```
 128 | 
 129 | *Keep the inference server running in the background for the next steps.*
 130 | 
 131 | 5.1. Check that you can run the orchestrator against the inference server
 132 | 
 133 | ```bash
 134 | uv run orchestrator @ configs/debug/orch.toml
 135 | ```
 136 | 
 137 | 5.2. Check that you can run evals against the inference server
 138 | 
 139 | ```bash
 140 | uv run eval @ configs/debug/eval.toml
 141 | ```
 142 | 
 143 | </details>
 144 | 
 145 | ### Additional Setup
 146 | 
 147 | 1. If you want to log your runs to [W&B](https://wandb.ai), log in
 148 | 
 149 | ```bash
 150 | uv run wandb login
 151 | # Or set `export WANDB_API_KEY=...`
 152 | ```
 153 | 
 154 | 2. If you require gated/ private models or datasets from [HuggingFace](https://huggingface.co), log in
 155 | 
 156 | ```bash
 157 | uv run hf auth login
 158 | # Or set `export HF_TOKEN=...`
 159 | ```
 160 | 
 161 | ## Training Examples
 162 | We provide end-to-end training examples in the [`examples`](examples) directory to highlight features of the framework and guide you through the process of training your own models.
 163 | 1. [**Reverse Text**](examples/reverse_text/README.md): Train `Qwen3-0.6B` to reverse a small chunk of text. Demonstrates tiny-scale single-turn SFT and RL training. Can be trained on a single consumer GPU in a few minutes, and is ideal for getting started.
 164 | 2. [**Wordle**](examples/wordle/README.md): Train `Qwen3-1.7B` to play Wordle. A fun example of multi-turn SFT and RL training. Can be trained on a 2-4 H100 GPUs in a few hours. Ideal for exploring the multi-turn training capabilities of the framework.
 165 | 3. [**Alphabet Sort**](examples/alphabet_sort/README.md): Train `Qwen3-4B-Instruct-2507` to sort names alphabetically. Demonstrates multi-turn RL training via LoRA without SFT warmup. Can be trained on a single H100 GPU in just over an hour. Ideal for exploring LoRA-based training.
 166 | 4. [**Wiki Search**](examples/wiki_search/README.md): Train `Qwen3-4B-Instruct-2507` to answer trivia questions by searching through a Wikipedia. Demonstrates multi-turn with web search tool use.
 167 | 5. [**Hendrycks Sanity**](examples/hendrycks_sanity/README.md): Run a sanity check experiment on `DeepSeek-R1-Distill-Qwen-1.5B` using a filtered subset of MATH where the model already partially solves 20-80% of problems. Useful for algorithm ablations.
 168 | 
 169 | *More to come...*
 170 | 
 171 | ## Docs
 172 | 
 173 | Check out the [docs](docs) directory for in-depth guides on how to use PRIME-RL.
 174 | 
 175 | - [**Entrypoints**](docs/entrypoints.md) - Overview of the main components (orchestrator, trainer, inference) and how to run SFT, RL, and evals
 176 | - [**Configs**](docs/configs.md) - Configuration system using TOML files, CLI arguments, and environment variables
 177 | - [**Environments**](docs/environments.md) - Installing and using verifiers environments from the Environments Hub
 178 | - [**Async Training**](docs/async.md) - Understanding asynchronous off-policy training and step semantics
 179 | - [**Logging**](docs/logging.md) - Logging with loguru, torchrun, and Weights & Biases
 180 | - [**Checkpointing**](docs/checkpointing.md) - Saving and resuming training from checkpoints
 181 | - [**Benchmarking**](docs/benchmarking.md) - Performance benchmarking and throughput measurement
 182 | - [**Deployment**](docs/deployment.md) - Training deployment on single-GPU, multi-GPU, and multi-node clusters
 183 | - [**Troubleshooting**](docs/troubleshooting.md) - Common issues and their solutions
 184 | 
 185 | ## Contributing
 186 | 
 187 | We warmly welcome community contributions! We use [issues](https://github.com/PrimeIntellect-ai/prime-rl/issues) to track bugs, feature requests, and share our internal roadmap. If you encounter bugs, have pain points during development, or have ideas for new features, please open an issue.
 188 | 
 189 | Contributions are welcome via PR. Please follow these guidelines:
 190 | 1. Install the [pre-commit hooks](#pre-commit-hooks) to ensure your code is formatted correctly.
 191 | 2. Please keep your PR in "Draft" until it is ready for review.
 192 | 3. If your PR resolves an issue, please link the issue in the PR description
 193 | 4. If you can, try running the [test suite](#tests) locally to ensure your changes are working as expected.
 194 | 
 195 | ### Pre-Commit Hooks
 196 | 
 197 | Please install the [pre-commit](https://pre-commit.com) hooks to ensure your code is formatted correctly.
 198 | 
 199 | ```bash
 200 | uv run pre-commit install
 201 | ```
 202 | 
 203 | ### Tests
 204 | 
 205 | Run the full test suite 
 206 | 
 207 | ```bash
 208 | uv run pytest -v
 209 | ```
 210 | 
 211 | To run unit tests, run
 212 | 
 213 | ```bash
 214 | uv run pytest tests/unit -v
 215 | ```
 216 | 
 217 | To run integration tests, run
 218 | 
 219 | ```bash
 220 | uv run pytest tests/integration -v
 221 | ```
 222 | 
 223 | To run CPU-only tests, use the inverse of the `gpu` marker:
 224 | 
 225 | ```bash
 226 | uv run pytest -v -m "not gpu"
 227 | ```
 228 | 
 229 | ## License
 230 | 
 231 | This project is licensed under the Apache 2.0 license, as found in the [License](LICENSE) file.
 232 | 
 233 | ## Citation
 234 | 
 235 | If you find our work useful, feel free to cite it using
 236 | 
 237 | ```tex
 238 | @misc{primeintellect2025prime-rl,
 239 |   author = {Prime Intellect},
 240 |   title = {PRIME-RL},
 241 |   url = {https://github.com/PrimeIntellect-ai/prime-rl},
 242 |   year = {2025}
 243 | }
 244 | ```
```


---
## skills/inference-server/SKILL.md

```
   1 | ---
   2 | name: inference-server
   3 | description: Start and test the prime-rl inference server. Use when asked to run inference, start vLLM, test a model, or launch the inference server.
   4 | ---
   5 | 
   6 | # Inference Server
   7 | 
   8 | ## Starting the server
   9 | 
  10 | Always use the `inference` entry point — never `vllm serve` or `python -m vllm.entrypoints.openai.api_server` directly. The entry point runs `setup_vllm_env()` which configures environment variables (LoRA, multiprocessing) before vLLM is imported.
  11 | 
  12 | ```bash
  13 | # With a TOML config
  14 | uv run inference @ path/to/config.toml
  15 | 
  16 | # With CLI overrides
  17 | uv run inference --model.name Qwen/Qwen3-0.6B --model.max_model_len 2048 --model.enforce_eager
  18 | 
  19 | # Combined
  20 | uv run inference @ path/to/config.toml --server.port 8001 --gpu-memory-utilization 0.5
  21 | ```
  22 | 
  23 | ## SLURM scheduling
  24 | 
  25 | The inference entrypoint supports optional SLURM scheduling, following the same patterns as SFT and RL.
  26 | 
  27 | ### Single-node SLURM
  28 | 
  29 | ```toml
  30 | # inference_slurm.toml
  31 | output_dir = "/shared/outputs/my-inference"
  32 | 
  33 | [model]
  34 | name = "Qwen/Qwen3-8B"
  35 | 
  36 | [parallel]
  37 | tp = 8
  38 | 
  39 | [slurm]
  40 | job_name = "my-inference"
  41 | partition = "cluster"
  42 | ```
  43 | 
  44 | ```bash
  45 | uv run inference @ inference_slurm.toml
  46 | ```
  47 | 
  48 | ### Multi-node SLURM (independent vLLM replicas)
  49 | 
  50 | Each node runs an independent vLLM instance. No cross-node parallelism — TP and DP must fit within a single node's GPUs.
  51 | 
  52 | ```toml
  53 | # inference_multinode.toml
  54 | output_dir = "/shared/outputs/my-inference"
  55 | 
  56 | [model]
  57 | name = "PrimeIntellect/INTELLECT-3-RL-600"
  58 | 
  59 | [parallel]
  60 | tp = 8
  61 | dp = 1
  62 | 
  63 | [deployment]
  64 | type = "multi_node"
  65 | num_nodes = 4
  66 | gpus_per_node = 8
  67 | 
  68 | [slurm]
  69 | job_name = "my-inference"
  70 | partition = "cluster"
  71 | ```
  72 | 
  73 | ### Dry run
  74 | 
  75 | Add `dry_run = true` to generate the sbatch script without submitting:
  76 | 
  77 | ```bash
  78 | uv run inference @ config.toml --dry-run true
  79 | ```
  80 | 
  81 | ## Custom endpoints
  82 | 
  83 | The server extends vLLM with:
  84 | 
  85 | - `/v1/chat/completions/tokens` — accepts token IDs as prompt input (used by multi-turn RL rollouts)
  86 | - `/update_weights` — hot-reload model weights from the trainer
  87 | - `/load_lora_adapter` — load LoRA adapters at runtime
  88 | - `/init_broadcaster` — initialize weight broadcast for distributed training
  89 | 
  90 | ## Testing the server
  91 | 
  92 | ```bash
  93 | curl http://localhost:8000/v1/chat/completions \
  94 |   -H "Content-Type: application/json" \
  95 |   -d '{
  96 |     "model": "Qwen/Qwen3-0.6B",
  97 |     "messages": [{"role": "user", "content": "Hi"}],
  98 |     "max_tokens": 50
  99 |   }'
 100 | ```
 101 | 
 102 | ## Key files
 103 | 
 104 | - `src/prime_rl/entrypoints/inference.py` — entrypoint with local/SLURM routing
 105 | - `src/prime_rl/inference/server.py` — vLLM env setup
 106 | - `src/prime_rl/configs/inference.py` — `InferenceConfig` and all sub-configs
 107 | - `src/prime_rl/inference/vllm/server.py` — FastAPI routes and vLLM monkey-patches
 108 | - `src/prime_rl/templates/inference.sbatch.j2` — SLURM template (handles both single and multi-node)
 109 | - `configs/debug/infer.toml` — minimal debug config
```


---
## skills/installation/SKILL.md

```
   1 | ---
   2 | name: installation
   3 | description: How to install prime-rl and its optional dependencies. Use when setting up the project, installing extras like deep-gemm for FP8 models, or troubleshooting dependency issues.
   4 | ---
   5 | 
   6 | # Installation
   7 | 
   8 | ## Basic install
   9 | 
  10 | ```bash
  11 | uv sync
  12 | ```
  13 | 
  14 | This installs all core dependencies defined in `pyproject.toml`.
  15 | 
  16 | ## All extras at once
  17 | 
  18 | The recommended way to install for most users:
  19 | 
  20 | ```bash
  21 | uv sync --all-extras
  22 | ```
  23 | 
  24 | This installs all optional extras (flash-attn, flash-attn-cute, etc.) in one go.
  25 | 
  26 | ## Mamba-SSM (NemotronH models)
  27 | 
  28 | For NemotronH (hybrid Mamba-Transformer-MoE) models, install `mamba-ssm` for Triton-based SSD kernels that match vLLM's precision:
  29 | 
  30 | ```bash
  31 | CUDA_HOME=/usr/local/cuda uv pip install mamba-ssm
  32 | ```
  33 | 
  34 | Requires `nvcc` (CUDA toolkit). Without `mamba-ssm`, NemotronH falls back to HF's pure-PyTorch implementation which computes softplus in bf16, causing ~0.4 KL divergence vs vLLM.
  35 | 
  36 | Note: do NOT install `causal-conv1d` unless your GPU architecture matches the compiled CUDA kernels. The code automatically falls back to PyTorch nn.Conv1d when it's absent.
  37 | 
  38 | ## FP8 inference with deep-gemm
  39 | 
  40 | For certain models like GLM-5-FP8, you need `deep-gemm`. Install it via the `fp8-inference` dependency group:
  41 | 
  42 | ```bash
  43 | uv sync --group fp8-inference
  44 | ```
  45 | 
  46 | This installs the pre-built `deep-gemm` wheel. No CUDA build step is needed.
  47 | 
  48 | ## Dev dependencies
  49 | 
  50 | ```bash
  51 | uv sync --group dev
  52 | ```
  53 | 
  54 | Installs pytest, ruff, pre-commit, and other development tools.
  55 | 
  56 | ## Key files
  57 | 
  58 | - `pyproject.toml` — all dependencies, extras, and dependency groups
  59 | - `uv.lock` — pinned lockfile (update with `uv sync --all-extras`)
```


---
## skills/toml-config/SKILL.md

```
   1 | ---
   2 | name: toml-config
   3 | description: How to write and use TOML configs in prime-rl. Use when creating config files, running commands with configs, or overriding config values via CLI.
   4 | ---
   5 | 
   6 | # TOML Config
   7 | 
   8 | All prime-rl commands use `pydantic_config` (tyro-backed) with TOML configs and CLI overrides.
   9 | 
  10 | ## Running with configs
  11 | 
  12 | ```bash
  13 | # Load a config file with @ syntax
  14 | uv run inference @ configs/debug/infer.toml
  15 | uv run sft @ configs/debug/sft/train.toml
  16 | uv run rl @ configs/debug/rl/train.toml
  17 | 
  18 | # CLI overrides (take precedence over TOML)
  19 | uv run inference @ config.toml --model.name Qwen/Qwen3-0.6B --server.port 8001
  20 | 
  21 | # Boolean flags: no value needed
  22 | uv run inference --model.enforce-eager          # sets to true
  23 | uv run inference --no-model.enforce-eager       # sets to false
  24 | 
  25 | # CLI-only (no TOML file)
  26 | uv run inference --model.name Qwen/Qwen3-0.6B --model.max-model-len 2048
  27 | 
  28 | # Compose multiple config files (later files override earlier ones)
  29 | uv run rl @ examples/reverse_text/rl.toml @ examples/reverse_text/slurm_rl.toml
  30 | 
  31 | # Nested config files: load a config for a specific section
  32 | uv run rl --model @ model.toml --data @ data.toml
  33 | ```
  34 | 
  35 | ## TOML structure
  36 | 
  37 | Top-level fields must come before any `[section]` header — this is a TOML rule.
  38 | 
  39 | ```toml
  40 | # Top-level fields first
  41 | gpu_memory_utilization = 0.5
  42 | seed = 42
  43 | 
  44 | # Then sections
  45 | [model]
  46 | name = "Qwen/Qwen3-0.6B"
  47 | max_model_len = 4096
  48 | 
  49 | [server]
  50 | port = 8000
  51 | ```
  52 | 
  53 | Putting a top-level field after a section header nests it inside that section, which causes validation errors.
  54 | 
  55 | ## Setting None
  56 | 
  57 | Use the string `"None"` in TOML to set a field to None:
  58 | 
  59 | ```toml
  60 | max_model_len = "None"
  61 | ```
  62 | 
  63 | ## SLURM mode
  64 | 
  65 | Both `rl` and `sft` commands support SLURM execution via an optional `[slurm]` section. When present, the run is submitted as a SLURM job instead of running locally.
  66 | 
  67 | SLURM configs are composed with the base config via CLI:
  68 | ```bash
  69 | uv run rl @ examples/reverse_text/rl.toml @ examples/reverse_text/slurm_rl.toml
  70 | ```
  71 | 
  72 | ### RL SLURM
  73 | 
  74 | ```toml
  75 | output_dir = "/shared/experiments/my-run"
  76 | 
  77 | [deployment]
  78 | type = "multi_node"
  79 | num_train_nodes = 2
  80 | num_infer_nodes = 1
  81 | gpus_per_node = 8
  82 | # nodes_per_fsdp_group = 1
  83 | 
  84 | [slurm]
  85 | job_name = "my-rl-job"
  86 | # dry_run = true          # generate script without submitting
  87 | # template_path = "path/to/custom.sh.j2"
  88 | # project_dir = "/path/to/project"
  89 | ```
  90 | 
  91 | When `[slurm]` is set for RL:
  92 | - `output_dir` must be explicitly set (the default `outputs` is rejected)
  93 | - Teacher inference is not supported in multi-node deployment
  94 | 
  95 | ### SFT SLURM
  96 | 
  97 | ```toml
  98 | output_dir = "/shared/experiments/my-sft-run"
  99 | 
 100 | [deployment]
 101 | type = "multi_node"
 102 | num_nodes = 2
 103 | gpus_per_node = 8
 104 | # nodes_per_fsdp_group = 1
 105 | 
 106 | [slurm]
 107 | job_name = "my-sft-job"
 108 | # dry_run = true
 109 | # template_path = "path/to/custom.sh.j2"
 110 | # project_dir = "/path/to/project"
 111 | ```
 112 | 
 113 | SFT deployment follows the same pattern as RL:
 114 | - `[deployment]` configures node/GPU allocation (`single_node` default or `multi_node`)
 115 | - `[slurm]` configures SLURM submission (job name, partition, template)
 116 | - `output_dir` must be explicitly set when using SLURM
 117 | - Multi-node deployment requires `[slurm]` to be set
 118 | 
 119 | ## SFT Distillation (Hard Distillation) With Teacher Rollouts
 120 | 
 121 | Use this when the teacher is an external OpenAI-compatible endpoint and you want to train from teacher completions directly (no teacher token logprobs required).
 122 | 
 123 | ```toml
 124 | [trainer.loss]
 125 | type = "sft"
 126 | 
 127 | [orchestrator]
 128 | use_token_client = false
 129 | 
 130 | [orchestrator.teacher_rollout_model.client]
 131 | base_url = ["https://your-openai-compatible-endpoint/v1"]
 132 | skip_model_check = true
 133 | 
 134 | [orchestrator.teacher_rollout_model.model]
 135 | name = "teacher-model-name"
 136 | ```
 137 | 
 138 | Notes:
 139 | - `orchestrator.teacher_rollout_model` switches rollout generation to the external teacher endpoint.
 140 | - `use_token_client = false` is required when `orchestrator.teacher_rollout_model` is set.
 141 | - `trainer.loss.type = "sft"` makes the RL trainer optimize masked NLL like SFT.
 142 | - In this mode, omit `[inference]`.
 143 | - Image input is supported when using a VLM student model and OpenAI-style image messages (`data:image/...`).
 144 | 
 145 | ## Available commands
 146 | 
 147 | All accept `@ config.toml` and CLI overrides:
 148 | 
 149 | | Command | Config class | Description |
 150 | |---------|-------------|-------------|
 151 | | `uv run rl` | full RL pipeline | Orchestrator + inference + trainer (local or SLURM) |
 152 | | `uv run inference` | `InferenceConfig` | vLLM inference server |
 153 | | `uv run trainer` | trainer config | RL trainer |
 154 | | `uv run orchestrator` | orchestrator config | Rollout orchestrator |
 155 | | `uv run env-server` | env server config | Environment server |
 156 | | `uv run sft` | SFT config | Supervised fine-tuning (local or SLURM) |
 157 | 
 158 | ## Key files
 159 | 
 160 | - `src/prime_rl/utils/config.py` — `BaseConfig`, `cli`, `get_all_fields`
 161 | - `src/prime_rl/entrypoints/rl.py` — unified RL entrypoint (local + SLURM)
 162 | - `src/prime_rl/configs/rl.py` — `RLConfig`, `SlurmConfig, DeploymentConfig`
 163 | - `src/prime_rl/entrypoints/sft.py` — unified SFT entrypoint (local + SLURM)
 164 | - `src/prime_rl/configs/sft.py` — `SFTConfig`
 165 | - `configs/` — all config files, organized by task
```
