# agentsmd-rl

RL training on SWE tasks from repositories with agent instruction files (AGENTS.md, CLAUDE.md, .cursorrules).

## Research Question

> Can we train coding agents to REASON about which repository instructions apply to a specific task, rather than blindly following all of them?

Repos have hierarchical config files (AGENTS.md, CLAUDE.md, SKILL.md) with 20-200+ rules at multiple directory levels. Many rules are irrelevant or even harmful for a specific PR. An agent that blindly follows everything wastes time or introduces errors.

**Key insight**: The PR author's choices — which conventions they follow vs. ignore — are the ground truth signal for instruction discrimination. We extract this signal as positive rubrics (rules the gold solution follows) and negative rubrics / distractors (rules that SEEM relevant but following them would produce worse code).

Grounded in: [NoisyBench](https://arxiv.org/abs/2601.07226) (80% drop from hard distractors), [RARE](https://arxiv.org/abs/2505.18761) (rationale-aware reward), [SkillsBench](https://arxiv.org/abs/2602.12670) (skill selection with distractors), [GSM-DC](https://arxiv.org/abs/2505.18761) (distractor training improves OOD robustness).

See [research/negative_rubrics_plan.md](research/negative_rubrics_plan.md) for the full research plan.

## Task Classes

The benchmark has two complementary task classes, both mined from merged PRs in repos with agent instruction files:

### Class A: Code Bug Fixes (`harbor_tasks/`, 775 tasks)

Standard SWE-bench-style tasks. The PR fixed a bug; the agent must reproduce the fix. Evaluation is purely execution-based: fail-to-pass tests must fail on the base commit and pass after the fix, pass-to-pass tests must pass on both.

### Class B: Code + Config Edits (`harbor_tasks_agentmd_edits/`, 232 tasks)

The PR changed both functional code AND agent instruction files (CLAUDE.md, AGENTS.md, SKILL.md, .cursorrules, etc.). These tasks test whether agents can navigate hierarchical config files — following relevant conventions, ignoring distracting ones, and updating config files correctly.

Evaluation uses 4 tracks (see below): hard tests, config edit comparison, positive rubric compliance, and distractor discrimination.

| | Class A (code-only) | Class B (code + config) |
|---|---|---|
| **Directory** | `harbor_tasks/` | `harbor_tasks_agentmd_edits/` |
| **Count** | 775 tasks (736 passing) | 232 tasks |
| **PR changes** | Code only | Code + agent config files |
| **Eval tracks** | Track 1 only | All 4 tracks |
| **Rubric rules** | Sometimes | 3.5/task avg (821 total) |
| **Distractors** | None | 1.7/task avg (388 total) |
| **What it measures** | Can the agent fix bugs? | Can the agent fix bugs AND reason about which config rules apply? |

Both classes share identical file structure and are processed by the same pipeline.

## Repository Structure

```
claude-code-rl-w-tinker/    # RL training library (proxy + GRPO + Tinker API)
taskforge/                   # Task construction toolkit (models, pipeline, judge, E2B worker)
  gemini_rubric_constructor.py  # Structured output rubric generation + Kimi validation loop
  hierarchy_context.py          # Config hierarchy extractor (root → leaf AGENTS.md)
  models.py                     # Pydantic: EvalManifest, Check, RubricRule, DistractorRule
harbor_tasks/                # Class A: code-only bug fixes (775 tasks)
harbor_tasks_agentmd_edits/  # Class B: code + config file edits (232 tasks)
scripts/                     # Batch pipeline launchers
research/                    # Research docs, negative rubrics plan
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

### Four-track evaluation (agentmd-edits)

| Track | What | Method | Coverage |
|-------|------|--------|----------|
| 1. Code correctness | Did the agent fix the bug? | `test.sh` → nop=0, gold=1 | 232/232 (100%) |
| 2. Config edits | Did the agent update config files correctly? | Gold diff vs agent diff (Gemini semantic comparison) | 223/232 (96%) |
| 3. Positive rubric | Does the agent follow relevant conventions? | LLM judge on diff vs rubric rules | 231/232 (100%) |
| 4. Distractors | Does the agent IGNORE irrelevant conventions? | Check agent didn't waste effort on collision rules | 185/232 (80%) |

**Track 4 collision types** (388 distractors across 185 tasks):
- `scope_ambiguity` (44%): rule's applicability is genuinely ambiguous for this PR
- `meta_confusion` (22%): writing ABOUT a pattern vs applying it
- `architecture_boundary` (15%): applying a pattern beyond its intended scope
- `rule_conflict` (13%): two valid rules conflict, agent must choose
- `would_cause_bug` (6%): following the rule introduces an error

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
| **4-track eval: code + config + rubric + distractors** | **Nobody** | **Yes (novel)** |
| **Negative rubrics (distractor discrimination)** | **Nobody** | **Yes (novel)** |
| **Hierarchical config context extraction** | **Nobody** | **Yes (novel)** |

## Status

**1,007 tasks** across two classes:
- 775 code-only (736 passing, 95%)
- 232 code+config with 4-track evaluation (175 with full 4-track coverage, 75%)

**Evaluation coverage (agentmd-edits):**
- 821 positive rubric rules (3.5/task), source-traced to config files
- 388 negative rubric / distractors (1.7/task), collision-typed and severity-graded
- Rubric generation via Gemini 3.1 Pro structured output (constrained decoding)
- Rubric validation via Kimi→Gemini→Kimi cross-validation loop

E2B agent-chain pipeline operational. 125 unit tests. RL training loop verified end-to-end with Qwen3.5-35B-A3B on Harbor.
