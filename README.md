# agentsmd-rl

RL training on SWE tasks from repositories with agent instruction files (AGENTS.md, CLAUDE.md, .cursorrules).

## Research Question

> Do AI coding agents perform differently on repositories that contain human-written agent guidance files? And can we use this signal for better RL training?

Every major SWE benchmark (SWE-Gym, SWE-rebench V2, SWE-Universe, SWE-Next) mines PRs from GitHub to build training environments. None of them control for whether the repository already had agent instruction files at task time. This is an unmeasured confounder that could affect both evaluation scores and post-training outcomes.

See [research/agent-manifest-confounding.md](research/agent-manifest-confounding.md) for the full analysis.

## Repository Structure

```
claude-code-rl-w-tinker/    # RL training library (proxy + GRPO + Tinker API)
taskforge/                   # Task construction toolkit (models, pipeline, judge)
harbor_tasks/                # Benchmark tasks: code-only bug fixes (~420 tasks)
harbor_tasks_agentmd_edits/  # Benchmark tasks: code + config file edits (~236 tasks)
scripts/                     # Scouting, filtering, migration scripts
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

### `harbor_tasks/` — Code Bug Fix Tasks

~420 Harbor-compatible tasks mined from merged PRs in repos with agent configs. Each task:
- `instruction.md` — bug description (what the agent sees)
- `environment/Dockerfile` — repo cloned at pre-fix commit
- `tests/test.sh` — deterministic tests → `/logs/verifier/reward.txt` (binary: 0 or 1)
- `eval_manifest.yaml` — check declarations with source traceability
- `solution/solve.sh` — gold patch (idempotent)
- `task.toml` — Harbor metadata

### `harbor_tasks_agentmd_edits/` — Code + Config Edit Tasks

~236 tasks where the PR changed both functional code AND agent config files (CLAUDE.md, AGENTS.md, etc.). Config edit quality is evaluated via LLM judge with gold references extracted from solve.sh, not exact string matching.

### `taskforge/` — Task Construction Toolkit

Python package for building and validating tasks:
- `models.py` — Pydantic models: `EvalManifest`, `Check`, `RubricRule`, `SourceRef`
- `config.py` — shared config patterns, `is_config_file()`, `extract_config_hunks()`
- `pipeline.py` — parallel pipeline orchestrator (`claude -p` against tasks)
- `judge.py` — LLM judge for config edit rubric (side-by-side gold vs agent diff)
- `e2b.py` — E2B sandbox validation
- `lint.py`, `filters.py`, `status.py` — quality checks

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

```bash
# Scout PRs from repos with agent configs
python scripts/scout_agentmd_prs.py --repos repos.txt --output scouted.jsonl

# Scaffold tasks (via Claude Code agent)
claude -p --agent task-scaffolder "owner/repo#123"

# Or batch scaffold
python -m taskforge.pipeline scaffold --workers 4

# Validate (Docker oracle: nop=0, gold=1)
python -m taskforge.pipeline validate --workers 8
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

~650 tasks across two datasets, ~400 passing validation. RL training loop verified end-to-end with Qwen3.5-35B-A3B on Harbor.
