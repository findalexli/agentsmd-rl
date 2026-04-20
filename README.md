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

### Class A: Code Bug Fixes (`harbor_tasks/`, 1,136 tasks)

Standard SWE-bench-style tasks. The PR fixed a bug; the agent must reproduce the fix. Evaluation is execution-based: fail-to-pass tests must fail on the base commit and pass after the fix, pass-to-pass tests must pass on both.

All 1,136 tasks also have **rubric rules** (3.8/task avg) and **distractors** (2.6/task avg) extracted from the repo's agent config files. These enable 4-track evaluation: programmatic tests + LLM-judged convention compliance + distractor discrimination. 952 tasks have the standalone LLM judge deployed directly into `test.sh`, so `harbor run` produces all 4 tracks in a single command.

### Class B: Code + Config Edits (`harbor_tasks_agentmd_edits/`, 6,167 tasks)

The PR changed both functional code AND agent instruction files (CLAUDE.md, AGENTS.md, SKILL.md, .cursorrules, etc.). These tasks test whether agents can navigate hierarchical config files — following relevant conventions, ignoring distracting ones, and updating config files correctly.

63 tasks currently passing oracle validation. This class is under active development.

| | Class A (code-only) | Class B (code + config) |
|---|---|---|
| **Directory** | `harbor_tasks/` | `harbor_tasks_agentmd_edits/` |
| **Count** | 1,136 tasks (1,131 passing, 99%) | 6,167 tasks (63 passing) |
| **PR changes** | Code only | Code + agent config files |
| **Eval tracks** | All 4 tracks | All 4 tracks |
| **Rubric rules** | 3,489 total (3.8/task avg) | Under development |
| **Distractors** | 1,710 total (2.6/task avg) | Under development |
| **What it measures** | Can the agent fix bugs AND follow the right conventions? | Can the agent fix bugs AND reason about which config rules apply AND update config files? |

Both classes share identical file structure and are processed by the same pipeline.

## Repository Structure

```
claude-code-rl-w-tinker/    # RL training library (proxy + GRPO + Tinker API)
taskforge/                   # Task construction toolkit
  models.py                     # Pydantic: EvalManifest, Check, RubricRule, DistractorRule
  judge.py                      # Track 3: rubric convention compliance judge (Gemini)
  distractor_judge.py           # Track 4: distractor discrimination judge (Gemini)
  standalone_judge.py           # Self-contained judge for inside harbor containers
  e2b_worker.py                 # E2B sandbox pipeline: agent-chain architecture
  backends.py                   # Multi-backend LLM pool with rate limit handling
  gemini_rubric_constructor.py  # Structured output rubric generation + Kimi validation
  hierarchy_context.py          # Config hierarchy extractor (root → leaf AGENTS.md)
harbor_tasks/                # Class A: code-only bug fixes (1,136 tasks)
harbor_tasks_agentmd_edits/  # Class B: code + config file edits (6,167 tasks)
scripts/
  run_agent_eval.py             # Agent eval runner (Track 1+3+4, pluggable backend)
  fix_task_toml.py              # Batch fix task.toml formatting issues
  deploy_judge.py               # Deploy standalone judge to all tasks
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
- `judge.py` — Track 3 rubric judge: evaluates agent code against repo conventions (Gemini 3.1 Pro)
- `distractor_judge.py` — Track 4 distractor judge: checks if agent incorrectly applied irrelevant rules
- `standalone_judge.py` — self-contained judge deployed inside harbor containers (no external deps)
- `e2b_worker.py` — E2B sandbox pipeline: agent-chain architecture (see below)
- `backends.py` — multi-backend LLM pool (MiniMax, GLM, Fireworks/Kimi) with auto-fallback, rate limit handling, and auto-resurrect
- `pipeline.py` — local parallel pipeline orchestrator (`claude -p` against tasks)
- `prompts/` — focused agent prompts (P2P enrich, improve tests, validate+fix)

### `research/`

- [agent-manifest-confounding.md](research/agent-manifest-confounding.md) — agent configs as unmeasured confounders
- [benchmark_construction_log.md](research/benchmark_construction_log.md) — detailed build log (phases 1-12)
- [pipeline-v2-plan.md](research/pipeline-v2-plan.md) — cost analysis and optimization plan
- [test-design-audit.md](research/test-design-audit.md) — test.sh design audit (SWE-bench Verified critique)

## Running Tasks

Requires [Harbor](https://github.com/laude-institute/harbor):

```bash
# Run a single task (all 4 tracks — programmatic + LLM judge)
harbor run -p harbor_tasks/<task> -a claude-code -m claude-opus-4-6 -e e2b -y

# Results in: <job-dir>/verifier/
#   reward.txt           — Track 1: binary 0/1 (programmatic tests)
#   agent.diff           — agent's code changes
#   track3_rubric.json   — Track 3: rubric convention compliance (Gemini)
#   track4_distractors.json — Track 4: distractor discrimination (Gemini)
```

### Agent Eval Runner (batch)

```bash
# Run N tasks with pluggable backend and 3-track scoring
.venv/bin/python scripts/run_agent_eval.py \
    --tasks tasks.txt \
    --out results.jsonl \
    --concurrency 4 \
    --backend anthropic \   # anthropic | minimax | glm
    --env e2b \
    --timeout 2400

# Outputs per-task JSONL + summary.json with pass rates
```

## Eval Results (April 18 2026)

### Opus 4.7 Baseline (10 tasks)

10 tier-A tasks from 10 different repos, evaluated on E2B with full 4-track scoring.

| Task | T1 (tests) | T3 (rubric) | T4 (distractors) | Time | Repo |
|------|-----------|-------------|-------------------|------|------|
| areal-data-proxy-batch-endpoint | **1** | 9/11 | 4/4 | 2.6m | inclusionAI/AReaL |
| sglang-diffusion-dtype-log-aggregation | 0 | 2/2 | 4/4 | 5.7m | sgl-project/sglang |
| clickhouse-cidb-secrets-refactor | 0 | 3/3 | 2/2 | 8.1m | ClickHouse/ClickHouse |
| playwright-mcp-press-enter-auto-snapshot | 0 | 0/3 | 5/5 | 8.3m | microsoft/playwright |
| vllm-rocm-uv-curl-failure | **1** | 3/3 | 2/2 | 10.7m | vllm-project/vllm |
| mimir-add-splitfile-claude-code-skill | 0 | 4/10 | 2/2 | 14.0m | grafana/mimir |
| nextjs-pr-status-reply-resolve | **1** | 6/6 | 2/2 | 14.6m | vercel/next.js |
| workers-sdk-ai-search-type-generation | 0 | 9/10 | 6/6 | 21.6m | cloudflare/workers-sdk |

### Kimi K2.5 vs Opus 4.7 (8 overlapping tasks)

| Metric | Kimi K2.5 (Fireworks) | Opus 4.7 (Anthropic) |
|--------|----------------------|---------------------|
| **Track 1 (solve rate)** | 1/8 (12.5%) | 3/8 (37.5%) |
| **Track 3 (rubric)** | 25/38 (65.8%) | 36/51 (70.6%) |
| **Track 4 (distractors)** | 21/21 (100%) | 27/27 (100%) |
| **Avg time** | 484s | 642s |

Key: Opus solves 3x more tasks. Kimi is 25% faster but produces no diff on the hardest task. Track 4 identical at 100% for both models.

### Known Limitations: Track 3/4 Quality (see audit below)

**Track 1 (programmatic tests) is the primary discriminator.** Tracks 3 and 4 have known quality issues that make their scores unreliable signals — see "Rubric Quality Audit" section.

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

### Four-track evaluation

| Track | What | Method | Coverage |
|-------|------|--------|----------|
| 1. Code correctness | Did the agent fix the bug? | `test.sh` → nop=0, gold=1 | 1,131/1,136 (99%) |
| 2. Config edits | Did the agent update config files correctly? | Gold diff vs agent diff (Gemini semantic comparison) | Class B only |
| 3. Positive rubric | Does the agent follow relevant conventions? | Gemini 3.1 Pro judges diff vs rubric rules | 914 tasks (3,489 rules) |
| 4. Distractors | Does the agent IGNORE irrelevant conventions? | Gemini checks agent didn't apply collision rules | 646 tasks (1,710 rules) |

Tracks 3 and 4 run automatically inside the harbor container via `standalone_judge.py` (deployed to 952 tasks). No external wrapper needed — `harbor run` produces all tracks.

**Track 4 collision types** (1,710 distractors across 646 tasks):
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

LLM calls inside sandboxes route through a multi-backend pool with automatic fallback and rate limit handling:

```
MiniMax M2.7    → 50 concurrent slots (primary, sustained 15 concurrent for 11+ hours)
GLM-5.1         → 30 concurrent slots (secondary)
Fireworks/Kimi  → 1-2 concurrent slots (per-account TPM limit, thinking tokens dominate)
```

**Rate limit handling** (redesigned Apr 18):
- Cooldown: 10s * 2^n, cap 120s (was 30s * 2^n, cap 600s)
- Auto-suspend backend after 20 consecutive 429s, auto-resurrect after 300s
- Single-shot `claude -p` calls (removed inner 4-attempt retry loop that caused 120x amplification)
- Staggered worker startup: `worker_id * 5s + random(0,3)` to prevent burst
- Re-enqueue delay: 30s * 2^n backoff (was immediate), max 4 retries

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
| **Negative rubrics (distractor discrimination)** | **Nobody** | **Yes (novel, 1,710 distractors)** |
| **Hierarchical config context extraction** | **Nobody** | **Yes (novel)** |
| **Self-contained LLM judge in test harness** | **Nobody** | **Yes (novel, Gemini structured output inside harbor)** |

## Status

**7,303 tasks** across two classes:
- 1,136 code-only (1,131 passing, 99%) — 952 with self-contained 4-track LLM judge
- 6,167 code+config (63 passing, under development)

**Quality tiers (code-only, based on 20-rubric quality audit via Opus 4.7):**
- **399 tier-A clean** — all quality rubrics pass (no solution leakage, no tautological tests, behavioral tests)
- **223 tier-A with full 4-track** — tier-A clean + rubric rules + distractors across 52 repos (RL-ready)
- 713 tier-A flagged — oracle works but known quality issues (leaky instructions, weak tests)

### RL-Ready Subset: 223 Tier-A Tasks with Full 4-Track Coverage

The highest quality subset — quality-audited, oracle-verified, with rubric + distractor rules across **52 repos**.

**Stats:**
- 960 rubric rules (4.3/task avg) — conventions from CLAUDE.md, AGENTS.md, SKILL.md
- 550 distractors (2.5/task avg) — rules that SEEM relevant but shouldn't apply

**Top repos** (10 of 52): gradio (21), transformers (20), opencode (18), AReaL (16), next.js (10), ruff (10), bun (9), uv (9), openclaw (8), playwright (8)

**Rubric categories:** style (15%), architecture (13%), documentation (5%), testing (4%), naming (4%), tooling (3%)

**Distractor collision types:**

| Type | Count | % | Description |
|------|-------|---|-------------|
| `scope_ambiguity` | 273 | 49% | Rule's applicability is genuinely ambiguous for this PR |
| `architecture_boundary` | 95 | 17% | Applying a pattern beyond its intended scope |
| `meta_confusion` | 91 | 16% | Writing ABOUT a pattern vs applying it |
| `rule_conflict` | 70 | 13% | Two valid rules conflict, agent must choose |
| `would_cause_bug` | 21 | 4% | Following the rule introduces an error |

**Distractor severity:** high (32%), medium (47%), low (20%)

**Sample rubric rules** (conventions the gold solution follows):
- _"After ANY Python code changes, ALWAYS run `make ruff`"_ — from `CLAUDE.md`
- _"Do not use browser-only APIs without environment guards"_ — from `SKILL.md`
- _"Keep framework-agnostic core logic separated from React/Solid bindings"_ — from `AGENTS.md`

**Sample distractors** (conventions that SEEM relevant but shouldn't apply):
- _"ALWAYS check this before writing data structures — use @record instead of @dataclass"_ — `rule_conflict`, severity: high
- _"Framework-agnostic core logic separated from React/Solid bindings"_ — `architecture_boundary`, severity: high
- _"Critical: Always run unit and type tests during development"_ — `scope_ambiguity`, severity: medium

**Evaluation infrastructure:**
- 3,489 positive rubric rules (3.8/task avg), source-traced to config files
- 1,710 negative rubric / distractors (2.6/task avg), collision-typed and severity-graded
- 612 tasks with full 4-track coverage (rubric + distractors + passing oracle)
- Rubric generation via Gemini 3.1 Pro structured output (constrained decoding) + Codex CLI extraction (100% line accuracy)
- Rubric validation via Kimi→Gemini→Kimi cross-validation loop
- Standalone LLM judge deployed into 952 tasks — `harbor run` produces all 4 tracks without external wrappers
- Agent eval runner (`scripts/run_agent_eval.py`) for batch evaluation with pluggable backends

### Rubric Quality Audit (April 19 2026)

Deep audit of all rubric and distractor rules across 8 eval tasks revealed systemic quality issues. **Track 3 (rubric) scores are currently noise, not signal. Track 4 (distractors) has a ceiling effect — both Opus and Kimi score 100%.**

**Smoking gun**: Kimi K2.5 scored 6/6 rubric on `nextjs-pr-status-reply-resolve` WITHOUT solving the task (T1=0). The rubric doesn't test convention-following — it tests whether the agent attempted the task at all.

**Five systemic pathologies (across 3,487 rubric rules):**

| Problem | Frequency | Description |
|---------|-----------|-------------|
| **Tautological rules** | ~50% | Restate what instruction.md says or what any correct solution does automatically |
| **Duplicate rules** | ~17% | Same rule 2-4x with slightly different phrasing (e.g., wildcard-import 4x in one task) |
| **Redundant with Track 1** | ~15% | Already tested by programmatic checks in test.sh |
| **Wrong line numbers** | ~30% | Source lines off by 3-16 lines; files exist (100% accurate) but cited lines contain unrelated content |
| **Wrong-scope distractors** | ~60% | Pulled from unrelated agent files (e.g., test-generator rules for framework source code) |

**Quantified field coverage (3,487 rubric rules across 914 manifests):**

| Field | Coverage |
|-------|----------|
| `source.path` | 73% |
| `source.lines` | 68% |
| `evidence` | 35% |
| `source_text` | 8% |
| `category` | 37% |

Distractors are well-formed (99%+ field coverage) but mostly implausible — no frontier model follows them.

**Root cause**: The rubric generation prompt asks "find rules the gold solution follows" without distinguishing pre-existing conventions from descriptions of what the PR does. Gemini correctly identifies that the gold uses `Info().get_secret()` and reports it as a "convention" — but it's just the task instruction restated.

**Required fixes (TODO):**
1. **Anti-tautology gate**: Reject rules semantically equivalent to instruction.md
2. **Dedup gate**: Collapse rules with >85% text similarity
3. **Track 1 redundancy gate**: Exclude rules already covered by programmatic checks
4. **Source verification gate**: Verify cited lines contain content related to the rule
5. **Distractor scope filter**: Only use config files from same package/directory as PR-modified files

Until these gates are implemented, **Track 1 is the only reliable evaluation signal.** Tracks 3 and 4 should be treated as experimental.

**Pipeline improvements (Apr 2026):**
- Retry stack redesign: eliminated 120x retry amplification (was 10×4×3 calls per rate limit)
- Multi-backend pool: MiniMax (primary) + GLM (secondary) with auto-fallback and auto-resurrect
- Staggered worker startup prevents burst rate limiting
- task.toml batch fixer: all 1,136 task configs now parse cleanly (fixed 222 broken files)
- Structural test audit: removed syntax-overfitting assertions (if/else keyword checks, exact variable assignments)

E2B agent-chain pipeline operational. RL training loop verified end-to-end with Qwen3.5-35B-A3B on Harbor.
