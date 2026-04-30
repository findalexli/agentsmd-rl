#!/usr/bin/env bash
set -euo pipefail

cd /workspace/areal

# Idempotency guard
if grep -qF "- `benchmark/` \u2014 Regression baselines, benchmark snapshots, and reference metric" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -4,10 +4,8 @@
 
 ## TL;DR for coding agents
 
-- **Runtime**: Designed for distributed GPU clusters (FSDP/Megatron + NCCL). Assume
-  containerized execution; no standalone local runs.
-- **Environment**: Platform images and launcher specs live under `launcher/` and
-  docs—reference them instead of hand-rolling virtualenvs.
+- **Runtime**: Designed for distributed GPU clusters (FSDP/Megatron + distributed
+  communication libraries). Assume containerized execution; no standalone local runs.
 - **Testing**: Integration and performance tests require multi-node hardware. Explain
   skips explicitly when you cannot access the cluster.
 - **Tooling**: `.pre-commit-config.yaml` runs Ruff (lint+format), mdformat,
@@ -19,84 +17,68 @@
   docs build pipeline.
 - **Legacy code**: `realhf/` is deprecated—do not modify or import from it; migrate uses
   into `areal/` equivalents instead.
+- **Collaboration**: Before editing code, outline the proposed plan and confirm it with
+  the user.
 
 When unsure, leave a `TODO(agent)` comment and note the constraint in your response.
 
 ## Repository map
 
-| Path                      | Purpose                                                                         |
-| ------------------------- | ------------------------------------------------------------------------------- |
-| `areal/api/`              | Core contracts: workflows, engines, controllers, schedulers, IO structs.        |
-| `areal/controller/`       | Distributed batching utilities and controller-side dataset packing.             |
-| `areal/core/`             | Async orchestration primitives (task runners, remote inference, workflow exec). |
-| `areal/dataset/`          | Dataset loaders & utilities that feed rollouts.                                 |
-| `areal/engine/`           | Training backends (FSDP2, Megatron, PPO actors) and inference adapters.         |
-| `areal/experimental/`     | Prototype engines/workflows; expect churn and breaking changes.                 |
-| `areal/launcher/`         | Orchestration entrypoints (local, Ray, Slurm) plus container specs.             |
-| `areal/models/`           | Model-specific adapters (Megatron-Core, Transformers wrappers).                 |
-| `areal/platforms/`        | Hardware/platform abstractions (CPU/GPU/NPU backends, runtime adapters).        |
-| `areal/reward/`           | Built-in reward functions plus helpers (math parsing, CLEVR counting).          |
-| `areal/scheduler/`        | Scheduler implementations and allocation logic.                                 |
-| `areal/tests/`            | Targeted tests; many require GPUs or mocked distributed backends.               |
-| `areal/thirdparty/`       | Vendored integrations (e.g., vLLM shims).                                       |
-| `areal/utils/`            | Logging (`stats_tracker`), tensor helpers, recovery, evaluation, device utils.  |
-| `areal/workflow/`         | Rollout/agent implementations (`multi_turn`, `rlvr`, `vision_rlvr`).            |
-| `examples/`               | Runnable entrypoints for math, multi-turn, RLHF, VLM, search agents.            |
-| `evaluation/`             | Offline evaluation scripts (math/code/Elo) and utilities.                       |
-| `functioncall/`           | Tool-calling utilities reused in workflows.                                     |
-| `docs/`                   | Jupyter Book source published to https://inclusionai.github.io/AReaL/.          |
-| `assets/`                 | Figures and other static assets.                                                |
-| `benchmark/`              | Regression baselines and benchmark snapshots.                                   |
-| `blog/`                   | Release and update write-ups.                                                   |
-| `csrc/`                   | CUDA/C++ extensions that need `build_ext --inplace` after edits.                |
-| `notebook/`               | Reference notebooks (outputs stripped by pre-commit).                           |
-| `patch/`                  | Local patches for third-party deps (e.g., SGLang fixes).                        |
-| `recipe/`                 | Deployment recipes and higher-level orchestration configs.                      |
-| `.pre-commit-config.yaml` | Hooks: Ruff lint/format, mdformat, clang-format, nbstripout, CLI docs.          |
-| `Dockerfile`              | Container recipe for the standard runtime environment.                          |
-| `realhf/`                 | Legacy integrations (read-only, do **not** modify or import).                   |
-
-### Where to find things
-
-- **`areal/api/`** – Contracts for engines, schedulers, dataloaders, and CLI configs.
-  Start here when adding new dataclasses or API surfaces.
-- **`areal/controller/`** – Distributed batching utilities and controller-side dataset
-  packing.
-- **`areal/core/`** – Async orchestration primitives (task runners, remote inference,
-  workflow execution).
-- **`areal/dataset/`** – Stateful data pipeline utilities. New datasets should plug into
-  these loaders for replay-safe iteration.
-- **`areal/engine/`** – Training and inference engines: FSDP2, Megatron, PPO actors, and
-  SGLang/vLLM adapters. Keep weight versioning logic consistent across edits.
-- **`areal/experimental/`** – Prototype engines/workflows; expect churn and breaking
-  changes.
-- **`areal/launcher/`** – Reference launchers for local, Ray, and Slurm targets plus
-  container specs; reuse these instead of ad-hoc scripts.
-- **`areal/models/`** – Model-specific adapters (Megatron-Core layers, Transformers
-  wrappers, custom heads).
-- **`areal/platforms/`** – Hardware/platform abstractions for CPU/GPU/NPU targets and
-  runtime adapters.
-- **`areal/reward/`** – Reward functions and math parsers. Wrap slow logic with
-  `AsyncRewardWrapper` in `areal/api/reward_api.py`.
-- **`areal/scheduler/`** – Placement and allocation policies for launchers; align with
-  `examples/**` configs.
-- **`areal/tests/`** – Unit and integration tests colocated with code; many require GPU
-  or mocked distributed backends.
-- **`areal/utils/`** – Cross-cutting helpers (logging, stats, tensor containers,
-  recovery, evaluation). Prefer reusing these utilities over duplicating logic.
-- **`areal/workflow/`** – Concrete rollout agents (`multi_turn`, `rlvr`, `vision_rlvr`).
-  Each illustrates how `RolloutWorkflow.arun_episode` should orchestrate inference and
-  rewards.
-- **`docs/`** – Jupyter Book source; mirrors the high-level architecture and
-  customization guides published at https://inclusionai.github.io/AReaL/.
-- **`evaluation/`** – Offline scoring pipelines that consume logged trajectories.
-- **`examples/`** – End-to-end wiring scripts for math, multi-turn, RLHF, VLM, and
-  search agents. Use them as references for config wiring and launcher usage.
-- **`functioncall/`** – Tool-calling scaffolding reused by workflows.
-- **`patch/`** – Maintains in-tree diffs applied to upstream dependencies; keep changes
-  minimal and well-documented.
-- **`realhf/`** – Legacy integrations retained for reference. Do **not** modify or
-  import; port call sites into `areal/` instead.
+- `areal/` — Core Python package housing APIs, controllers, engines, workflows, and
+  shared utilities:
+  - `areal/api/` — Contracts for workflows, engines, schedulers, IO structs, and
+    CLI/config dataclasses.
+  - `areal/controller/` — Distributed batching and controller-side dataset packing
+    helpers.
+  - `areal/core/` — Async orchestration primitives for task runners, remote inference,
+    and workflow execution.
+  - `areal/dataset/` — Stateful dataset loaders and utilities that feed rollout jobs
+    safely.
+  - `areal/engine/` — Training/inference backends (FSDP2, Megatron, PPO actors, remote
+    adapters).
+  - `areal/experimental/` — Prototype engines/workflows that evolve quickly; expect
+    breaking changes.
+  - `areal/launcher/` — Launch specs for local, Ray, and Slurm clusters plus container
+    guidance.
+  - `areal/models/` — Model-specific adapters (Megatron-Core layers, Transformers
+    wrappers, custom heads).
+  - `areal/platforms/` — Hardware/platform abstractions for CPU/GPU/NPU runtimes and
+    device adapters.
+  - `areal/reward/` — Built-in reward functions, math parsers, and helpers (wrap slow
+    logic with AsyncRewardWrapper).
+  - `areal/scheduler/` — Placement and allocation policies aligned with launcher
+    configs.
+  - `areal/tests/` — Focused unit/integration suites (many require GPUs or mocked
+    distributed backends).
+  - `areal/thirdparty/` — Vendored integrations (e.g., vLLM/SGLang shims) kept in-tree.
+  - `areal/tools/` — Developer utilities and maintenance scripts tied to the core
+    package.
+  - `areal/utils/` — Cross-cutting helpers for logging, tensor ops, stats tracking,
+    checkpoints, and recovery.
+  - `areal/workflow/` — Concrete rollout agents (`multi_turn`, `rlvr`, `vision_rlvr`)
+    implementing `RolloutWorkflow`.
+- `assets/` — Figures and other static assets referenced across docs and blogs.
+- `benchmark/` — Regression baselines, benchmark snapshots, and reference metrics (e.g.,
+  `verl_v0_3_0_post1_*`).
+- `blog/` — Release notes and update write-ups documenting project progress.
+- `csrc/` — CUDA/C++ extensions (run `build_ext --inplace` or reinstall editable wheels
+  after edits).
+- `docs/` — Jupyter Book source for https://inclusionai.github.io/AReaL/ plus CLI
+  reference generators.
+- `evaluation/` — Offline scoring pipelines (math, code, Elo) and shared
+  evaluators/utilities.
+- `examples/` — End-to-end wiring scripts for math, RLHF, VLM, multi-turn, search
+  agents, and launcher recipes.
+- `functioncall/` — Tool-calling scaffolding reused by workflows and evaluation
+  harnesses.
+- `notebook/` — Reference notebooks (outputs stripped via pre-commit) for quick
+  experimentation.
+- `patch/` — In-tree patches applied to third-party dependencies (e.g., SGLang
+  hotfixes).
+- `realhf/` — Legacy integrations kept read-only; do **not** modify or import in new
+  code.
+- `recipe/` — Deployment recipes and higher-level orchestration configs per target
+  environment.
 
 ## Distributed operations & tooling
 
@@ -109,8 +91,8 @@ When unsure, leave a `TODO(agent)` comment and note the constraint in your respo
 - **Secrets & endpoints**: Credentials for remote inference (SGLang, vLLM, Redis, etc.)
   are managed outside the repo. Flag their absence rather than hardcoding replacements.
 - **Testing limitations**: End-to-end tests (FSDP, Megatron, distributed RPC) require
-  multi-node NCCL clusters. If you cannot execute them, state that your validation is
-  limited to static analysis/doc updates.
+  multi-node clusters using distributed communication libraries. If you cannot execute
+  them, state that your validation is limited to static analysis/doc updates.
 - **Formatting & docs**: Pre-commit runs Ruff (lint+format), mdformat, clang-format,
   nbstripout, and CLI doc generation. Run `pre-commit run --all-files` (or install the
   hook) before submitting; keep doc edits aligned with the Jupyter Book structure in
@@ -179,148 +161,186 @@ Reference docs:
 
 ### Add or adjust a rollout workflow
 
-1. Create/modify a class in `areal/workflow/` that subclasses `RolloutWorkflow`.
-1. Maintain async behavior (`async def arun_episode`); gather trajectories per prompt
-   and return padded tensors (typically via `concat_padded_tensors`).
-1. Expose knobs via `__init__` (tokenizer, `GenerationHyperparameters`, reward fn,
-   dump_dir).
-1. Update references in entry scripts or configs (e.g.,
-   `examples/multi-turn-math/train.py`).
+- Start from the existing patterns in `areal/workflow/multi_turn.py`, `rlvr.py`, or
+  `vision_rlvr.py`, then add a sibling module under `areal/workflow/` that subclasses
+  `RolloutWorkflow`.
+- In `__init__`, thread through `GenerationHyperparameters`, the tokenizer, reward
+  callable, stat scope, and optional `dump_dir`; wrap the reward via
+  `AsyncRewardWrapper` exactly like `MultiTurnWorkflow` does.
+- Keep `arun_episode` async-only, drive generation through `InferenceEngine.agenerate`,
+  and emit tensors using `concat_padded_tensors` so outputs stay
+  `[batch, seq_len, ...]`.
+- Use `areal/utils/data.py` helpers for padding/broadcasting, `areal/utils/logging` for
+  logger plumbing, and `stats_tracker` for reward metrics.
+- Persist transcripts under `{dump_dir}/{engine.get_version()}/` (follow the
+  `multi_turn` implementation) when debugging is enabled.
+- Update whichever entry script or launcher references the workflow (e.g.,
+  `examples/multi-turn-math/train.py`, configs in `examples/**/conf/`, or CLI glue) so
+  Hydra can import the new module.
 
 ### Introduce a reward function
 
-1. Implement reward logic in `areal/reward/<name>.py`.
-1. Register via `areal/reward/__init__.py` or supply a fully qualified import path in
-   configs.
-1. For slow reward evaluation, wrap with `AsyncRewardWrapper` to avoid blocking rollout
-   loops.
+- Create `areal/reward/<name>.py` and implement a callable following
+  `areal/api/reward_api.py` (see `geometry3k_reward_fn` for reference).
+- Accept `(prompt, completions, prompt_ids, completion_ids, **data)` and return a
+  scalar; extract answers deterministically (`math_parser.math_equal`, regex, etc.) and
+  avoid blocking I/O.
+- Add the identifier to `VALID_REWARD_FN` and branch selection logic in
+  `areal/reward/__init__.py` so configs like `reward.path=...` resolve automatically.
+- When rewards rely on slow models or external services, keep the heavy code inside the
+  reward module but let workflows wrap it with `AsyncRewardWrapper` (as in
+  `MultiTurnWorkflow`).
+- Document required dataset fields or endpoints in the module docstring/README so launch
+  scripts can provision secrets or caches.
 
 ### Wire a new dataset
 
-1. Place dataset loader under `areal/dataset/` (follow existing patterns using
-   `StatefulDataLoader`).
-1. Update config fields (`train_dataset.*`) to point to the new loader and schema.
-1. Ensure prompts provide the keys expected by your workflow (`messages`, `answer`,
-   etc.).
+- Mirror the layout in `areal/dataset/gsm8k.py`, `clevr_count_70k.py`, etc.: create
+  `areal/dataset/<name>.py` with `get_<name>_<type>_dataset` helpers for SFT/RL
+  variants.
+- Update `areal/dataset/__init__.py` by appending the dataset to `VALID_DATASETS` and
+  adding a dispatch branch inside `_get_custom_dataset`.
+- Define the sample schema explicitly (`messages`, `answer`, `image_path`, metadata) and
+  validate it before returning; filter/trim sequences with tokenizer-aware checks when
+  `max_length` is provided.
+- Expose configuration knobs (path, split, type, max_length, processor/tokenizer
+  requirements) via the `DatasetConfig` dataclass in `areal/api/cli_args.py`, then
+  reference them in the relevant `examples/**/conf` YAML.
+- If preprocessing or external storage is required, add a short note beside the loader
+  or under `examples/<recipe>/README.md` so other agents know how to stage data.
 
 ### Launch training / evaluation
 
-- Follow the launcher examples in `examples/**` together with the matching scripts in
-  `launcher/`. Each example README points to the expected scheduler (local, Ray, or
-  Slurm) and container image.
-- Always keep rollout/inference versioning in sync via `WeightUpdateMeta` (see
-  `examples/multi-turn-math/train.py`). Document any skipped launcher steps if you
-  cannot access the target cluster.
+- Choose an existing script in `examples/**` (math, multi-turn, VLM, etc.) that mirrors
+  your use case, then replicate its launcher pairing (`areal/launcher/local.py`,
+  `ray.py`, `slurm.py`, or `sglang_server.py`).
+- Read the example README to collect scheduler requirements, container images,
+  environment variables, and any dataset preparation steps before running.
+- Keep rollout actors and inference engines version-aligned by propagating
+  `WeightUpdateMeta` (as shown in `examples/multi-turn-math/train.py`) and noting
+  skipped weight updates explicitly if clusters are unavailable.
+- Capture the Hydra/CLI overrides you used
+  (`python ... +train_dataset.path=... engine.type=...`) inside the PR/test plan so runs
+  are reproducible.
+- When cluster access is blocked, document which launcher stages were skipped and what
+  validation (unit tests, static checks) you ran instead.
 
 ### Publish docs
 
-- The docs site builds via Jupyter Book pipelines defined in `docs/`. Coordinate with
-  maintainers before triggering a build and note in responses when doc rebuilds are
-  deferred due to environment constraints.
+- Place prose in the right section under `docs/` (tutorial, algorithms, customization,
+  lite, etc.) and update `_toc.yml` so Jupyter Book exposes the new page.
+- Run `mdformat` (or `mdformat --check`) on edited Markdown plus `ruff format` on
+  embedded code blocks when needed.
+- Regenerate CLI docs with `python docs/generate_cli_docs.py` whenever
+  `areal/api/cli_args.py` or CLI entrypoints change, then restage
+  `docs/cli_reference.md`.
+- Coordinate a docs build (or explain why it is skipped) and capture the limitation in
+  your PR/testing notes if the hosted pipeline cannot run.
+
+### Monitor metrics & artifacts
+
+- Emit rollout/training metrics through `areal/utils/stats_tracker.py`; grab a scoped
+  tracker (`stats_tracker.get("rollout")`) and log scalars so downstream `StatsLogger`
+  backends (W&B/SwanLab) pick them up automatically.
+- When debugging, pass `dump_dir` into workflows so transcripts persist under
+  `{dump_dir}/{engine.get_version()}/` like `areal/workflow/multi_turn.py`; scrub
+  sensitive data before committing artifacts.
+- Checkpoint via `areal/utils/saver.py` and resume with `areal/utils/recover.py`; note
+  the checkpoint path and version in your PR/test notes so others can reproduce the
+  exact state.
 
 ## Testing & validation strategy
 
-- **Unit tests**: Suites under `areal/tests/` frequently rely on GPUs or mocked
-  distributed backends. If you cannot execute them, state which files would normally be
-  run (e.g., `test_utils.py`, `test_allocation_mode.py`).
-- **Workflow smoke tests**: `areal/tests/grpo` covers rollout logic but requires GPUs;
-  acknowledge skipped coverage explicitly.
-- **Distributed/FSDP suites**: `test_fsdp_*`, `test_sglang_engine.py`, and RPC suites
-  demand multi-node NCCL clusters. Mention the dependency when deferring.
-- **Static checks**: Pre-commit enforces Ruff lint/format, mdformat, clang-format,
-  nbstripout, CLI doc regeneration, and autoflake. Call out when hooks cannot be run
-  locally.
+### Create or extend unit tests
+
+- Place new tests under `areal/tests/` using `test_<topic>.py` so Pytest auto-discovers
+  them (e.g., tensor helpers live in `test_utils.py`, schedulers in
+  `test_local_scheduler.py`).
+- Reuse fixtures + helpers: copy the pattern from `test_utils.py` (local fixtures
+  feeding parametrized cases) or import shared logic from `areal/tests/utils.py`
+  (`is_in_ci`, `get_bool_env_var`). Prefer `pytest.fixture` + `pytest.mark.parametrize`
+  over ad-hoc loops.
+- Keep tests hermetic by mocking engines/workflows similar to
+  `test_engine_api_workflow_resolution.py`; avoid spinning up real clusters unless you
+  are under `torchrun/` or `experimental/`.
+- For GPU/distributed requirements, gate with `pytest.mark.skipif` or custom env checks
+  (see `test_fsdp_engine_nccl.py` and `areal/tests/torchrun/`), and document the
+  hardware dependency inside the skip reason.
+- When tests need sample artifacts (configs, datasets), reuse the examples in
+  `areal/tests/sft` or `areal/tests/grpo` rather than downloading new assets. Commit
+  only lightweight fixtures.
+
+### Run the right suites
+
+- **Unit suites**: Target the file you touched, e.g.,
+  `pytest areal/tests/test_utils.py`. If a full run is infeasible, list the exact
+  command you would have executed.
+- **Workflow smoke tests**: `areal/tests/grpo` exercises rollout loops and expects CUDA;
+  acknowledge when skipped.
+- **Distributed/FSDP suites**: `test_fsdp_*`, `test_sglang_engine.py`, RPC/torchrun
+  folders require multi-node setups and distributed communication libraries. Call out
+  the limitation explicitly.
+- **Static checks**: Pre-commit runs Ruff lint/format, mdformat, clang-format,
+  nbstripout, CLI doc regeneration, and autoflake. Note if hooks were not run locally
+  and why.
 
 Always mention resource requirements in PRs and in agent responses when tests are
 skipped.
 
-## Observability & ops
-
-- `areal/utils/stats_tracker.py` collects metrics; `StatsLogger` streams to W&B/SwanLab.
-- `areal/utils/saver.py` + `areal/utils/recover.py` handle checkpoints/resume.
-- Rollout workflows can persist transcripts by passing `dump_dir`; outputs are organized
-  by weight version.
-- `evaluation/` hosts offline evaluation scripts (math, code, Elo). They expect
-  generated logs in standard formats—consult `evaluation/README.md`.
-
-## Known constraints & best practices
-
-- Large downloads: models/datasets fetched via Hugging Face; ensure cache directories
-  point to shared storage in multi-node runs.
-  - `HF_HOME` sets the root directory for all Hugging Face cache data (models, datasets,
-    etc.).
-  - `TRANSFORMERS_CACHE` (if set) overrides the model cache location only, and takes
-    precedence over `HF_HOME` for model files.
-  - Prefer setting `HF_HOME` for a unified cache; use `TRANSFORMERS_CACHE` only if you
-    need to separate model files from other cache data.
-- Async training relies on weight versioning—never mutate versions manually; call
-  `set_version`/`update_weights` like the examples.
-- Avoid blocking operations inside workflows; perform heavy I/O via `aiofiles` or
-  background tasks.
-- Respect the distributed launchers. For new scripts, prefer using existing launch
-  utilities over bespoke `torchrun` commands.
-- When editing CUDA/C++ extensions, run `pip install -e .` again or
-  `python setup.py build_ext --inplace`.
-
-## Collaboration conventions
-
-- **Issue first**: Tie every PR to a filed issue using `Fixes #123` or `Refs #123` in
-  the description. Follow the GitHub issue templates under `.github/ISSUE_TEMPLATE/`.
-- **Branch naming**: Use kebab-case summaries, e.g., `feature/multi-turn-metrics` or
-  `bugfix/fsdp-weight-sync`.
-- **Commit messages**:
-  - Prefer [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/)
-    prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
-  - Keep the subject ≤72 characters; use imperative mood (“fix rollout metric”) and add
-    a body explaining *why* when the change is non-trivial.
-  - Squash noisy WIP commits before pushing; keep history clean for bisects.
-- **PR titles**: Mirror the main change using the same prefix style, e.g.,
-  `feat: add discounted reward stats tracker hook`.
-- **PR checklist**:
-  - Summarize the change, highlight risks (e.g., breaking changes, performance impacts,
-    compatibility issues), list test commands run (or clearly state why tests are
-    skipped).
-  - Link related documentation updates; mention resource requirements for GPU-bound
-    tests.
-  - Add screenshots or log snippets when touching user-facing outputs.
-- **Reviews**: Be explicit about follow-ups with `TODO(agent)` comments and track them
-  in the PR discussion. Address review feedback with additional commits (no force-push
-  once review starts unless requested).
-- **Pre-merge**: Ensure pre-commit hooks pass (Ruff lint+format, mdformat, clang-format,
-  nbstripout, CLI docs, autoflake). For doc-only changes, run `mdformat --check` on
-  touched files.
-
-## Reviewer checklist
-
-- **Scope & requirements**: Confirm the PR maps to a filed issue and the description
-  lists clear acceptance criteria. Ensure major behavior changes are covered by tests or
-  documented.
-- **Testing evidence**: Look for explicit test commands (unit, integration, or docs
-  builds). Verify GPU-heavy suites are marked/skipped appropriately with rationale.
-- **Asynchrony & concurrency**: For workflow or engine edits, check that async functions
-  await all I/O, avoid blocking calls, and keep weight versioning (`set_version`,
-  `update_weights`) consistent.
-- **Resource awareness**: Ensure configs note memory/GPU expectations, and new
-  datasets/models document storage paths or cache requirements.
-- **Code style compliance**: Watch for Ruff lint/format alignment, autoflake cleanup,
-  clang-format on CUDA/C++, mdformat for docs, logging via `areal.utils.logging`, and
-  consistent type hints/dataclass usage.
-- **Config & docs**: Validate new knobs land in the right dataclasses/YAMLs with
-  defaults explained in docs or README snippets. Cross-check hyperlinks and CLI
-  references.
-- **Observability**: Confirm metrics integrate with `stats_tracker`/`StatsLogger`, and
-  long-running workflows expose dump directories or debugging hooks when warranted.
-- **Cleanup & debt**: Reject lingering debug prints, commented code, or unexplained
-  `TODO`s (except tagged `TODO(agent)` with context). Ensure migrations include
-  recovery/evaluator updates if they impact checkpoints.
+## Collaboration & review expectations
+
+- **Branches**: Use kebab-case summaries (e.g., `feature/multi-turn-metrics`,
+  `bugfix/fsdp-weight-sync`) so PR automation and reviewers can parse intent quickly.
+- **Commits**: Follow Conventional Commit prefixes (`feat:`, `fix:`, `docs:`, etc.),
+  keep the subject around 72 characters for readable logs (go longer only when the extra
+  context is essential), write in imperative voice, and put deeper reasoning in the
+  body. Squash noisy WIP commits before opening or updating a PR.
+- **Pre-merge checks**: Run the full pre-commit stack (Ruff lint+format, mdformat,
+  clang-format, nbstripout, CLI docs, autoflake). For doc-only edits, at least run
+  `mdformat --check` on touched files and call out anything you could not run locally.
+- **Surface scope upfront**: Tie the PR to a filed issue, summarize acceptance criteria,
+  highlight risk areas (breaking changes, performance regressions), and note any
+  configs, datasets, or launchers impacted.
+- **Testing evidence**: List the exact commands you executed (unit, workflow smoke, docs
+  build). When hardware is unavailable, state the skipped suites, why they were skipped,
+  and what alternative validation (static analysis, mocks) you performed.
+- **Async + resource safety**: When touching workflows/engines, confirm async code
+  awaits I/O, avoids blocking calls, and preserves weight versioning
+  (`set_version`/`update_weights`). Document memory/GPU expectations and dataset or
+  checkpoint storage requirements inside the PR/test notes.
+- **Style, config & docs**: Ensure Ruff/clang-format/autoflake output is clean. Thread
+  new options through the right dataclasses/YAMLs, update docs/CLI references, and
+  verify hyperlinks. Mention any formatting gaps you plan to address later via
+  `TODO(agent)`.
+- **Observability & cleanup**: Keep metrics flowing through `stats_tracker`/
+  `StatsLogger`, expose dump directories when debugging, and remove stray debug prints
+  or commented code. Note migrations or recovery steps when checkpoints or evaluators
+  change so reviewers know what to verify.
 
 ## Reference material
 
-- Docs portal: https://inclusionai.github.io/AReaL/
-- Quickstart tutorial: `docs/tutorial/quickstart.md`
-- Customization guides: `docs/customization/`
-- Best practices: `docs/best_practices/` (debugging, OOM handling, rollout tips)
-- Release notes: `docs/version_history.md`
-
-Create an issue or discussion if you hit unclear architecture boundaries—this repo
-evolves quickly.
+- **Docs portal** (`https://inclusionai.github.io/AReaL/`): Hosted Jupyter Book with the
+  full table of contents; use it to cross-check rendered diagrams, formulas, and links.
+- **Tutorials & quickstart** (`docs/tutorial/quickstart.md`): End-to-end GSM8K GRPO run
+  covering single-node LocalLauncher flows, Ray/Slurm deployment knobs, SkyPilot
+  recipes, and the legacy→lite config converter.
+- **Lite deep dive** (`docs/lite/gsm8k_grpo.md`): Architecture-level walkthrough of how
+  launchers, RemoteSGLangEngine, workflows, and FSDP PPO actors coordinate during
+  asynchronous GRPO on GSM8K; great for understanding control flow before editing
+  engines or workflows.
+- **Customization guides** (`docs/customization/*.md`): Step-by-step patterns for adding
+  datasets, authoring new `RolloutWorkflow` subclasses, or wiring custom RL algorithms
+  while keeping configs Hydra-friendly.
+- **Algorithm notes** (`docs/algorithms/*.md`): Reference math + configuration advice
+  for GRPO, DAPO/DAPO-style filters, async RL, GSPO, LitePPO, m2po, rloo, etc.,
+  including when to switch between synchronous and asynchronous modes.
+- **Best practices** (`docs/best_practices/*.md`): Practical debugging playbooks,
+  reward-drift diagnostics, OOM mitigation, and performance profiling checklists you
+  should cite when explaining skipped tests or perf limitations.
+- **CLI & doc tooling** (`docs/cli_reference.md`): Auto-generated CLI argument catalog
+  plus instructions for regenerating docs/CLI output before landing config changes.
+- **Benchmarks & reproducibility** (`docs/references/*.md`): Canonical benchmark setups,
+  dataset/model combos, and experiment-log expectations to mention in PR validation
+  notes.
+- **Version history** (`docs/version_history.md`): Release timeline noting major API
+  moves, deprecations, and migration steps from legacy AReaL to AReaL-lite.
PATCH

echo "Gold patch applied."
