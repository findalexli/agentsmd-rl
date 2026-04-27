# agentsmd-rl

RL training on SWE tasks from repositories with agent instruction files (AGENTS.md, CLAUDE.md, .cursorrules).

## Research Question

> Can we train coding agents to REASON about which repository instructions apply to a specific task, rather than blindly following all of them?

Repos have hierarchical config files (AGENTS.md, CLAUDE.md, SKILL.md) with 20-200+ rules at multiple directory levels. Many rules are irrelevant or even harmful for a specific PR. An agent that blindly follows everything wastes time or introduces errors.

**Key insight**: The PR author's choices — which conventions they follow vs. ignore — are the ground truth signal for instruction discrimination. We extract this signal as positive rubrics (rules the gold solution follows) and negative rubrics / distractors (rules that SEEM relevant but following them would produce worse code).

Grounded in: [NoisyBench](https://arxiv.org/abs/2601.07226) (80% drop from hard distractors), [RARE](https://arxiv.org/abs/2505.18761) (rationale-aware reward), [SkillsBench](https://arxiv.org/abs/2602.12670) (skill selection with distractors), [GSM-DC](https://arxiv.org/abs/2505.18761) (distractor training improves OOD robustness).

See [research/negative_rubrics_plan.md](research/negative_rubrics_plan.md) for the full research plan.

## Task taxonomy

A merged PR is useful for the benchmark only when its gold fix is **causally shaped by the repo's agent-instruction files** (CLAUDE.md / AGENTS.md / SKILL.md / .cursor/rules / etc.). A Gemini 3.1 Pro judge sorts every candidate PR into four buckets (rates from the 2026-04-26 scout pass over 13,046 PRs):

| Class | Gold diff | What it tests | Share |
|---|---|---|---|
| **A — edits a tier-1 file** | Includes changes to CLAUDE.md / AGENTS.md / SKILL.md / `.cursor/rules`. | "Can the agent update agent-instruction files correctly?" | 1.6% (204) |
| **B — code follows a rule** | Code-only, but the fix encodes a rule documented in a tier-1 file (e.g. "use 7-char commit hashes", "no wildcard imports"). | "Can the agent reason about which conventions apply to this fix?" | 4.2% (546) |
| C — decorative *(discarded)* | Code-only fix determined purely by the bug; removing the markdown wouldn't change the fix. | (nothing instruction-specific) | 79.7% (10,398) |
| D — unscaffoldable *(discarded)* | Platform-specific (iOS / Windows / GPU), >500-line refactor, no testable behavior. | (cannot become a Linux Docker benchmark) | 14.5% (1,896) |

**A + B are kept** — complementary. C and D are discarded.

Type B is roughly 2.7× the size of A and is the more important bucket conceptually: **most agent-instruction-following happens without the agent ever editing the markdown** — it manifests in the choices the agent makes inside the code.

All tasks get the same 4-track evaluation: programmatic fail-to-pass + pass-to-pass tests, plus a self-contained Gemini judge in `test.sh` that scores convention compliance (positive rubric) and distractor avoidance (negative rubric).

### Where tasks live on disk (snapshot 2026-04-27)

| Folder | Active | Quarantined | Notes |
|---|---|---|---|
| `harbor_tasks/` | 582 (Type A+B, code-fix) | — | Opus 4.7 scaffolded, 92.8% Docker-oracle pass (540 / 582), 89% rubric pass |
| `harbor_tasks_md_authoring/` | **718** (706 HIGH + 12 MEDIUM) | 170 (DELETE/LOW + 2 secret-pattern) | Deterministic scaffold + Gemini quality gate (v2 pipeline). All 718 have GHCR images. |
| `harbor_tasks_agentmd_edits/` | 81 (code + config edits, Track 2) | — | Smaller, harder corpus |

The two flagship corpora — `harbor_tasks/` (code) and `harbor_tasks_md_authoring/` (markdown-authoring) — together hold **1,300 active tasks**, all with pre-built Docker images on GHCR.

## How tasks are filtered

We run two parallel pipelines, distinguished by what the gold diff modifies:

- **Pipeline A — code-fix** (→ `harbor_tasks/`). PR's diff is code; the fix encodes a rule documented in a tier-1 file (or *is* the agent's update to such a file). Scaffolded with **Claude Opus 4.7** inside an isolated sandbox so it can read the repo and design a behavioral test.
- **Pipeline B — markdown-authoring** (→ `harbor_tasks_md_authoring/`). PR's diff is *only* tier-1 instruction files. Scaffolded **deterministically** (no LLM): shallow-clone at base SHA, apply the gold patch, generate `test_outputs.py` that greps for the most distinctive `+` lines. The Gemini judge serves as the quality gate.

Both pipelines start with the same discovery + scout machinery (GitHub topic search, `gh pr list --json files,…` with limit ≤ 200), then diverge on classification, scaffolding method, and quality gate.

| | Pipeline A (code-fix) | Pipeline B (markdown-authoring) |
|---|---|---|
| Latest scout | 2026-04-26 (147 repos, 12-month window) | 2026-04-27 (1,037 repos, 24-month window) |
| Raw merged PRs fetched | 19,417 | 29,733 |
| After scout-time filters | 14,549 unique | 9,629 candidates |
| Pre-classifier filter | Tier-1 *repo* allowlist | Tier-1 *path* regex (every changed file must match) |
| Classifier | Gemini per-PR causality judge → A / B / C / D / ERR | Two-stage Gemini judge: pre-judge by title, post-judge by full gold patch |
| Survivors after classifier | A=204 + B=546 = 750 (5.7%) | 302 KEEP / 19 DROP from the 321 that passed the regex |
| Scaffold | Opus 4.7 + Docker oracle (≈25-30% scaffold-fail) | Deterministic, ≈99% success |
| Cumulative active corpus | **582** (92.8% Docker oracle pass) | **718** (706 HIGH + 12 MEDIUM after post-judge) |

**End-to-end yield**: ≈3% for Pipeline A, ≈7.5% for Pipeline B. Pipeline B is higher because the path-regex pre-filter starts from a much narrower distribution — anything reaching the LLM judges is already pure-tier-1.

For the rigorous breakdown — exact regex, every drop count, per-row decision logs — see [`research/data_mining_pipeline.md`](research/data_mining_pipeline.md).

### What the post-judge drops in Pipeline B

Of 822 markdown-authoring tasks scaffolded across all 2026-04-27 passes (608 pre-existing + 214 new):

| Verdict | Count | % | Outcome |
|---|---|---|---|
| **HIGH** | 706 | 85.9% | Keep — concrete behavioral rule, specific commands/paths, low slop |
| **MEDIUM** | 12 | 1.5% | Keep — plausible but generic-leaning |
| LOW | 2 | 0.2% | Quarantine — marginal value, decorative |
| DELETE | 102 | 12.4% | Quarantine — bot-generated PRs, generic skill slop, broken-yaml manifests, dummy-test PRs |

The post-judge is the strictest filter — it sees the complete gold patch and PR description. The pre-judge (title-only) catches a much smaller share of slop (19 of 321 pure-tier-1 PRs ≈ 6%) because it has no body or patch context.

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
harbor_tasks/                # Class A: code-only bug fixes (226 active)
harbor_tasks_quarantine/     # Quarantined tasks + Class B candidate pool
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

- [rubric-reward-postmortem.md](research/rubric-reward-postmortem.md) — why LLM-generated rubrics failed as reward signal, trace-derived alternative
- [agent-manifest-confounding.md](research/agent-manifest-confounding.md) — agent configs as unmeasured confounders
- [test-design-audit.md](research/test-design-audit.md) — test.sh design audit (SWE-bench Verified critique)
- [benchmark_construction_log.md](research/benchmark_construction_log.md) — detailed build log (phases 1-12)
- [negative_rubrics_plan.md](research/negative_rubrics_plan.md) — distractor conventions research plan
- [pipeline-v2-plan.md](research/pipeline-v2-plan.md) — pipeline architecture optimization plan

## Pre-Built Docker Images

Task environments are distributed as pre-built images on GitHub Container Registry to avoid Docker Hub rate limits (100 pulls/6hr) and slow rebuilds.

```bash
# Pull a task image directly
docker pull ghcr.io/findalexli/agentsmd-rl/<task-name>:latest

# Harbor auto-pulls when docker_image is set in task.toml
harbor run -p harbor_tasks/<task> -a claude-code -m claude-opus-4-6 -y
```

Images are built via GitHub Actions (`gh workflow run push-images.yml`) — no local Docker builds needed. Each image is tagged with both a Dockerfile content hash (for cache-busting) and `:latest`. Harbor falls back to building from `environment/Dockerfile` if no pre-built image is configured.

Both task corpora are kept on GHCR:
- `harbor_tasks/` — code-fix tasks
- `harbor_tasks_md_authoring/` — markdown-authoring tasks (all 718 active tasks have images as of 2026-04-27)
- `harbor_tasks_agentmd_edits/` — code + config edit tasks (Track 2)

All Dockerfiles use shallow clone (`git fetch --depth=1 origin <SHA>`) for fast builds and small images.

| Registry | Why |
|----------|-----|
| **ghcr.io** (chosen) | Free for public packages, no pull rate limits, native GitHub Actions auth |
| Docker Hub | 100 pulls/6hr unauthenticated — breaks parallel eval runs |
| ECR Public | 50 GB free storage, too small for 400+ images |

See `scripts/push_images.py` for the build+push script and `.github/workflows/push-images.yml` for the CI workflow.

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

## Research Insights

Key findings from building this benchmark, documented in `research/`:

### LLM-generated rubrics don't work as reward signal

We tried three generators (Gemini, Kimi validation loop, Codex/GPT-5.4) to extract convention-following rubrics from agent config files. After generating 3,489 rules across 914 tasks and running a controlled 8-task evaluation, we found that **rubric scores do not discriminate between agents that solve the task and agents that don't**. ~50% of rules are tautological (describe what any correct solution does), and the core problem — distinguishing "pre-existing convention" from "description of the gold solution" — is irreducibly circular when deriving rules from the gold diff.

**Decision:** Binary outcome reward only. Rubrics demoted to monitoring/diagnostics.
**Future direction:** Derive rubrics from multi-agent trace diffs (what do successful agents do that failed ones don't?) instead of from the gold diff.
[Full analysis →](research/rubric-reward-postmortem.md)

### Agent instruction files are unmeasured confounders

Repos with CLAUDE.md/AGENTS.md files are systematically different from repos without them — more active, better documented, stricter CI. This means any performance difference between "tasks from config repos" and "tasks from non-config repos" could be explained by repo quality, not agent instruction awareness. We control for this by sourcing ALL tasks from config repos and varying only the instructions shown to the agent.
[Full analysis →](research/agent-manifest-confounding.md)

### SWE-bench-style test design is fragile

Following [OpenAI's critique of SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/), we audited test design across 100+ tasks and found that structural assertions (exact variable names, AST patterns, grep for specific strings) reject valid alternative solutions. Our design principle: test BEHAVIOR not STRUCTURE. Structural checks are supplementary only (<=40% weight), and every fail-to-pass test must invoke the actual code path.
[Full analysis →](research/test-design-audit.md)

### Generating hard, non-trivial rubrics is an open problem

Even after fixing extraction accuracy (Codex achieves 100% line accuracy), the fundamental challenge remains: most repo conventions are either trivially followed by any competent agent (formatting, imports) or too ambiguous to judge automatically (architecture decisions). The ~4% of rules that genuinely test convention *discrimination* — where an agent must choose between competing conventions — are the ones that matter for RL training, and we don't yet have a reliable way to generate them at scale.

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

| Track | What | Method | Role | Coverage |
|-------|------|--------|------|----------|
| 1. Code correctness | Did the agent fix the bug? | `test.sh` → nop=0, gold=1 | **Reward signal** | All Class A tasks |
| 2. Config edits | Did the agent update config files correctly? | Gold diff vs agent diff (Gemini semantic comparison) | Monitoring | Class B only |
| 3. Positive rubric | Does the agent follow relevant conventions? | Gemini 3.1 Pro judges diff vs rubric rules | Monitoring | 914 tasks (3,489 rules) |
| 4. Distractors | Does the agent IGNORE irrelevant conventions? | Gemini checks agent didn't apply collision rules | Monitoring | 646 tasks (1,710 rules) |

**Only Track 1 contributes to the RL reward.** Tracks 2-4 are logged for diagnostics and model comparison but do not affect training gradients. See [Research Insights](#research-insights) for why.

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

We run two simple pipelines, both inside an E2B Firecracker microVM with Docker access. **Each pipeline uses one `claude -p` agent call** — the agent does its own iteration internally (write code → run Docker → verify → adjust) instead of being orchestrated across multiple separate calls.

### Pipeline 1: Repair (existing task → cleaned task)

For tasks already in `harbor_tasks/` that have quality issues (broken oracle, weak tests, leaky instructions). Used to clean the active pool.

```
[ Programmatic lint ] → [ One Opus call: fix tests + instruction + run Docker oracle + write verdict ]
```

- Programmatic lint (no LLM, ~2s) flags issues like tautological tests, unpinned deps, `pip install` at test time. Output is fed to the Opus prompt as a "what's wrong" hint.
- The Opus agent reads `quality.json`, edits `test_outputs.py` / `instruction.md` / `eval_manifest.yaml`, runs `nop=0/gold=1` Docker validation itself, and writes either `{"fixed": true, "nop_reward": 0, "gold_reward": 1}` or `{"abandoned": true, "reason": "..."}` to `reconcile_status.json`. We trust the agent's verdict and download.
- Empirically: ~85–90% real pass rate, 15–25 min wall per task.

```bash
.venv/bin/python scripts/validate_batch.py \
    --task-file queue.txt \
    --start-at oneshot_repair \
    --concurrency 10
```

### Pipeline 2: Scaffold (new PR → new task)

For PRs in the candidate placeholder pool that pass the causality judge. (Currently the same `claude -p` repair pattern; a dedicated `oneshot_scaffold` mode is planned that internalizes the lint rules + Docker oracle in a single agent call.)

### Why one-call pipelines

Earlier versions of this repo had a 4–6 node chain (scaffold → enrich → improve → validate → judge → reconcile → tests-rewrite). Each node spun a fresh sandbox session, each hit rate limits independently, and a redundant validate node frequently overwrote the agent's correct verdict. Collapsing to a single call makes the pipeline ~5× more accurate and substantially easier to reason about.

The legacy multi-node modes (`fix_quality`, `validate`, `judge`) still exist in `taskforge/e2b_worker.py` and are reachable via `--start-at <mode>`, but `oneshot_repair` is the supported default.

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

## Status (2026-04-26)

**Active scaffolded tasks (`harbor_tasks/`):** 442 total / **399 tier-A** quality-audited. 91 of these were freshly scaffolded overnight via the `oneshot_scaffold` pipeline (45% pass rate from a 204-PR queue). Tier-A images now being built and pushed to ghcr.io via the `push-images.yml` workflow.

**Candidate PR pool ready for scaffolding:** **977 PRs** classified as A (direct tier-1 edit) or B (code follows a rule). Composed of:
- 204 baseline (Class B / 4,809-stub audit, mostly mature)
- 750 from today's deep scout (107 repos, 19,417 fetched → 13,046 judged → A=204, B=546)
- 23 from prior recovery batches (ERR retries + C-unfetchable retries)

**In flight:**
- Scout against 40 newly-discovered repos (n8n, anthropics/skills, openai/codex, gemini-cli, etc.) — projected to add 100-300 more candidate PRs once Flex-judged.
- Dockerfile shallow-clone migration: 198 of the 442 tasks updated to `git fetch --depth=1` (saves ~17× on initial fetch). Image rebuild in progress on GHCR.

**Switched all classifier work from Gemini batch → Flex tier (sync, 9 req/s sustained).** A 9,171-prompt batch that ran 3+ hours stalled out; re-submitted on Flex finished in 17 min.

See [research/scouting_report_2026_04_26.md](research/scouting_report_2026_04_26.md) for the full breakdown — yields per repo, classifier comparison, batch-vs-Flex experiment, etc.

### Monitoring: Convention-Following Rubrics (Tracks 3 & 4)

Rubric and distractor rules are generated for diagnostics and model comparison, not reward. They help understand *how* agents solve tasks but don't reliably discriminate solved vs unsolved (see [postmortem](research/rubric-reward-postmortem.md)).

**Coverage (across 914 tasks with rubric data):**
- 3,489 positive rubric rules (3.8/task avg) — conventions from CLAUDE.md, AGENTS.md, SKILL.md
- 1,710 negative rubric / distractors (2.6/task avg) — collision-typed and severity-graded
- 952 tasks with self-contained LLM judge in test.sh (Gemini structured output)

**Distractor collision types:**

| Type | Count | % | Description |
|------|-------|---|-------------|
| `scope_ambiguity` | 273 | 49% | Rule's applicability is genuinely ambiguous for this PR |
| `architecture_boundary` | 95 | 17% | Applying a pattern beyond its intended scope |
| `meta_confusion` | 91 | 16% | Writing ABOUT a pattern vs applying it |
| `rule_conflict` | 70 | 13% | Two valid rules conflict, agent must choose |
| `would_cause_bug` | 21 | 4% | Following the rule introduces an error |

**Evaluation infrastructure:**
- Rubric generation via Gemini 3.1 Pro structured output + Codex CLI extraction (100% line accuracy)
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

**Decision: outcome-only reward, rubrics as monitoring.**

We attempted multiple fixes — Codex/GPT-5.4 extraction (fixed line drift, 100% accuracy), Kimi→Gemini→Kimi validation loop (caught 25-75% of hallucinations), anti-tautology gates (caught obvious cases). These improved precision but didn't solve the core problem: tautological rules are *technically correct*, they just don't test anything meaningful. The boundary between "convention the solution follows" and "description of the solution" is irreducibly fuzzy.

Track 1 (binary outcome from programmatic tests) is the sole RL reward signal. Tracks 3 and 4 are logged for diagnostics — useful for understanding *how* an agent solved a task, not *whether* it did. See [research/rubric-reward-postmortem.md](research/rubric-reward-postmortem.md) for the full analysis and future direction (trace-derived rubrics from multi-agent runs).

**Pipeline improvements (Apr 2026):**
- Retry stack redesign: eliminated 120x retry amplification (was 10×4×3 calls per rate limit)
- Multi-backend pool: MiniMax (primary) + GLM (secondary) with auto-fallback and auto-resurrect
- Staggered worker startup prevents burst rate limiting
- task.toml batch fixer: all 1,136 task configs now parse cleanly (fixed 222 broken files)
- Structural test audit: removed syntax-overfitting assertions (if/else keyword checks, exact variable assignments)

E2B agent-chain pipeline operational. RL training loop verified end-to-end with Qwen3.5-35B-A3B on Harbor.
