# agentsmd-rl

RL training on SWE tasks from repositories with agent instruction files (AGENTS.md, CLAUDE.md, .cursorrules).

## Research Question

> Do AI coding agents perform differently on repositories that contain human-written agent guidance files? And can we use this signal for better RL training?

Every major SWE benchmark (SWE-Gym, SWE-rebench V2, SWE-Universe, SWE-Next) mines PRs from GitHub to build training environments. None of them control for whether the repository already had agent instruction files at task time. This is an unmeasured confounder that could affect both evaluation scores and post-training outcomes.

See [research/agent-manifest-confounding.md](research/agent-manifest-confounding.md) for the full analysis.

## Task Classes

The benchmark has two complementary task classes, both mined from merged PRs in repos with agent instruction files:

### Class A: Code Bug Fixes (`harbor_tasks/`, ~630 tasks)

Standard SWE-bench-style tasks. The PR fixed a bug; the agent must reproduce the fix. Evaluation is purely execution-based: fail-to-pass tests must fail on the base commit and pass after the fix, pass-to-pass tests must pass on both.

### Class B: Code + Config Edits (`harbor_tasks_agentmd_edits/`, ~350 tasks)

The PR changed both functional code AND agent instruction files (CLAUDE.md, AGENTS.md, SKILL.md, .cursorrules, etc.). These tasks test whether agents can follow and update the repo's own guidance files. Evaluation adds a rubric judge layer: an LLM checks whether the gold solution's config edits follow the style/convention rules declared in `eval_manifest.yaml`.

| | Class A (code-only) | Class B (code + config) |
|---|---|---|
| **Directory** | `harbor_tasks/` | `harbor_tasks_agentmd_edits/` |
| **PR changes** | Code only | Code + agent config files |
| **eval_manifest checks** | `pr_diff`, `repo_tests`, `static` | Also `agent_config` with source refs |
| **Rubric rules** | Sometimes | Almost always |
| **Rubric judge** | Optional | Required (ICR >= 0.8) |
| **What it measures** | Can the agent fix bugs? | Can the agent fix bugs AND maintain config files? |

Both classes share identical file structure and are processed by the same pipeline.

## Repository Structure

```
claude-code-rl-w-tinker/    # RL training library (proxy + GRPO + Tinker API)
taskforge/                   # Task construction toolkit (models, pipeline, judge, E2B worker)
harbor_tasks/                # Class A: code-only bug fixes (~630 tasks)
harbor_tasks_agentmd_edits/  # Class B: code + config file edits (~350 tasks)
scripts/                     # Batch pipeline launchers
research/                    # Research docs and analysis
.claude/skills/              # Claude Code skills for task scaffolding/validation
.claude/agents/              # Headless agent definitions for batch pipelines
```

### `claude-code-rl-w-tinker/` — Training Library

RL training using Claude Code as the agent harness and Tinker API for GPU compute.

```
Claude Code CLI (Harbor sandbox)
    │ Anthropic Messages API
    ▼
anthropic_proxy.py → captures (token_ids, logprobs) at generation time
    │
    ▼
Tinker SamplingClient → remote GPU (Qwen3.5, Kimi K2.5, etc.)
    │
    ▼
train.py → Harbor Trial → reward → GRPO → Tinker forward_backward
```

Key design: logprobs captured at generation time (not post-hoc), per-turn datums (AReaL "individual" style), Harbor as a black box. See [claude-code-rl-w-tinker/README.md](claude-code-rl-w-tinker/README.md) for architecture details.

### Task File Structure (both classes)

Each task directory contains:
- `instruction.md` — bug description (what the agent sees)
- `environment/Dockerfile` — repo cloned at pre-fix commit
- `tests/test.sh` → `test_outputs.py` — deterministic tests → `/logs/verifier/reward.txt` (binary: 0 or 1)
- `eval_manifest.yaml` — check declarations with source traceability + rubric rules
- `solution/solve.sh` — gold patch (idempotent)
- `task.toml` — Harbor metadata (difficulty, source PR, timeouts)
- `status.json` — validation provenance (per-node model/backend/time, history)

### `taskforge/` — Task Construction Toolkit

Python package for building and validating tasks:
- `models.py` — Pydantic models: `EvalManifest`, `Check`, `RubricRule`, `SourceRef`
- `config.py` — shared config patterns, `is_config_file()`, `extract_config_hunks()`
- `pipeline.py` — local parallel pipeline orchestrator (`claude -p` against tasks)
- `e2b_worker.py` — E2B sandbox pipeline: agent-chain architecture (see below)
- `judge.py` — rubric judge for config edit quality (eval_manifest.yaml rubric rules)
- `backends.py` — multi-backend LLM pool (GLM, Fireworks/Kimi, OAuth) with auto-fallback
- `prompts/` — focused agent prompts (P2P enrich, improve tests, validate+fix)

### `research/`

- [agent-manifest-confounding.md](research/agent-manifest-confounding.md) — agent configs as unmeasured confounders
- [benchmark_construction_log.md](research/benchmark_construction_log.md) — detailed build log (phases 1-12)
- [pipeline-v2-plan.md](research/pipeline-v2-plan.md) — cost analysis and optimization plan
- [test-design-audit.md](research/test-design-audit.md) — test.sh design audit (SWE-bench Verified critique)

## Running Tasks

Requires [Harbor](https://github.com/laude-institute/harbor):

```bash
# Build and validate a task
docker build -t harbor-<task>:latest harbor_tasks/<task>/environment/
harbor run -p harbor_tasks/<task> -a claude-code -m claude-opus-4-6 -n 1

# Or use the validation skill
# /validate-task <task-name>
```

## Training

```bash
export TINKER_API_KEY=tml-...

python claude-code-rl-w-tinker/train.py \
    --model_name Qwen/Qwen3.5-35B-A3B \
    --agent_name claude-code \
    --environment_type docker \
    --max_turns 200 \
    --groups_per_batch 4 \
    --group_size 4
```

## Evaluation Architecture

### Scoring: Binary

All checks must pass → reward `1`. Any check fails → reward `0`.
This matches every major SWE benchmark (SWE-bench, Terminal Bench, SWE-smith, R2E-Gym).

### Check types

| Type | What | Example |
|------|------|---------|
| `fail_to_pass` | Must fail on base commit, pass after fix | Bug reproduction test |
| `pass_to_pass` | Must pass before and after fix | Regression test |

### Two-tier evaluation (agentmd-edits)

| Tier | Method | What |
|------|--------|------|
| Code tests | `test.sh` → binary reward | Did the code fix work? |
| Config rubric | LLM judge with gold reference | Did the agent update configs correctly? |

### Design principles

Following [OpenAI's critique of SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/):

- **No narrow tests** that enforce specific variable names or API choices from the gold patch
- Accept multiple valid implementations — test BEHAVIOR, not STRUCTURE
- Structural AST checks supplementary only (<=40% weight)

## Task Construction Pipeline

### E2B Agent-Chain Pipeline (primary)

Each task runs through 4 focused `claude -p` agents inside an E2B Firecracker microVM with Docker:

```
[Scaffold] → [P2P Enrich] → [Improve Tests] → [Validate+Fix] → [Rubric Judge]
```

| Agent | What it does | Docker access? |
|-------|-------------|----------------|
| **P2P Enrich** | Discover repo CI/CD, add pass-to-pass tests | Yes (runs CI commands) |
| **Improve Tests** | Upgrade grep-only tests to behavioral subprocess tests | No |
| **Validate+Fix** | Docker build → NOP test (expect 0) → Gold test (expect 1) → fix issues | Yes (builds & runs containers) |
| **Rubric Judge** | Check config edits against eval_manifest.yaml rubric rules | No (programmatic) |

Inter-agent communication via `status.json` — each agent reads previous nodes' notes, writes its own findings with model/backend provenance.

```bash
# Validate all unvalidated tasks (80 concurrent E2B sandboxes)
set -a && source .env && set +a && export GH_TOKEN=$(gh auth token)
.venv/bin/python scripts/validate_batch.py --concurrency 80

# Only tasks from last 24 hours
.venv/bin/python scripts/validate_batch.py --recent 24 --concurrency 80
```

### Backend Pool

LLM calls inside sandboxes route through a multi-backend pool with automatic fallback:

```
Tier 0: GLM-5.1 (free)        → 40 concurrent slots
Tier 1: Kimi K2.5 / Fireworks → 40 concurrent slots (fallback on GLM 429)
```

Rate-limited tasks auto-retry (up to 2x) on a different backend.

### Local Pipeline (legacy)

```bash
# Scout PRs from repos with agent configs
python -m taskforge.scout scout --agentmd --repos-file scouted_repos.jsonl --output scouted.jsonl

# Scaffold tasks (via Claude Code agent)
python -m taskforge.pipeline scaffold-from-prs --input scouted.jsonl --workers 8 --pool
```

## Differentiation from Existing Work

| What | Who Does It | Do We? |
|------|------------|--------|
| Mine PRs → Docker environments | SWE-rebench, SWE-Universe, SWE-Next | Yes (standard) |
| Fail-to-pass test verification | SWE-bench (all variants) | Yes (standard) |
| RL training from PR environments | SWE-Gym, SWE-RL, DeepSWE | Yes |
| **Filter for repos with agent configs** | **Nobody** | **Yes (novel)** |
| **Dual reward: execution + config adherence** | **Nobody** | **Yes (novel)** |
| **Measure agent-config confounding** | **Nobody** | **Yes (novel)** |

## Status

~978 tasks across two classes (631 code-only + 347 code+config), 649 passing Docker oracle validation. E2B agent-chain pipeline operational. RL training loop verified end-to-end with Qwen3.5-35B-A3B on Harbor.
