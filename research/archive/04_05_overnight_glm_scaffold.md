# AgentMD Scaffold Campaign — 2026-04-05/06

## Goal
Scaffold new `markdown_edits` tasks. Target: 500+ total (currently 236 existing).

## Status (updated 2026-04-06 15:30 PDT)

### Phase A: New Scaffolds — COMPLETE

| Run | Backend | Input | Success | Skip | Fail | Notes |
|-----|---------|-------|---------|------|------|-------|
| GLM re-scaffold | GLM-5.1 | 119 critical | 33 | 8 | 78 | Rate limited after ~42 tasks |
| OAuth retry | Claude OAuth | 78 failed | 51 | 27 | 0 | Perfect run, 0 failures |
| **Total** | | **119** | **84** | **35** | **0** | 71% success, 29% skip |

### Phase B: Cleanup — COMPLETE

- Deleted 136 old broken template dirs (stubs, placeholders, syntax errors)
- Fixed 6 syntax errors (unicode chars, orphaned code) in remaining tasks
- Stamped `source_repo`/`source_pr` in 132 task.toml files
- Fixed 132 malformed toml lines (concatenated fields)

### Current Numbers

| Metric | Count |
|--------|-------|
| Total task dirs | 283 |
| Structurally clean | 283 (100%) |
| GOOD (behavioral tests) | 109 (38%) |
| OK (subprocess or 3+ structural) | 25 (8%) |
| WEAK (grep-only, no code execution) | 147 (51%) |
| BAD (missing files) | 2 (<1%) |

### Key Finding: Prompt Improvements Work

| Cohort | GOOD rate | Notes |
|--------|-----------|-------|
| Today's scaffolds (improved prompts) | **77%** (59/76) | $15 budget, skeleton-then-fill |
| Older scaffolds (old prompts) | **24%** (50/207) | $6-8 budget, no examples |

The prompt improvements (skeleton-then-fill, gold examples, subprocess requirements, higher budget) **tripled** the GOOD rate from 24% → 77%.

---

## Phase C: Improve Weak Tests — IN PROGRESS

### Problem
147 tasks have grep-only tests (read file → check string). These don't reliably distinguish base (broken) from fixed code. Need behavioral tests that execute code via `subprocess.run()`.

### Approach
Created `taskforge/prompts/improve_tests.md` — takes an existing WEAK task and rewrites f2p tests to use code execution while preserving p2p/agent_config tests.

Registered as `improve-tests` action in `taskforge/pipeline.py` ($10 budget, opus model).

### Execution Plan

**Split 147 WEAK tasks between GLM and OAuth running concurrently:**

| Batch | Backend | Tasks | Workers | Budget | Timeout |
|-------|---------|-------|---------|--------|---------|
| A | GLM-5.1 | 83 | 4 | $10/task | 1800s |
| B | Claude OAuth | 84 | 4 | $10/task | 1800s |

GLM will hit its 5-hour cap after ~35-40 tasks. When that happens:
- GLM failures → retry with API key (pay-per-token)
- Or wait for GLM cap reset and re-run

**Pipeline command:**
```bash
# GLM batch
.venv/bin/python -m taskforge.pipeline improve-tests \
  --task-dir markdown_edits \
  --tasks "$GLM_TASKS" --workers 4 --budget 10.0 --timeout 1800

# OAuth batch (concurrent, separate terminal)
.venv/bin/python -m taskforge.pipeline improve-tests \
  --task-dir markdown_edits \
  --tasks "$OAUTH_TASKS" --workers 4 --budget 10.0 --timeout 1800
```

### Quality Gate (post-improvement)

After each batch, run automated audit:
```python
# Must have: subprocess.run() or _run() helper
# Must have: assert on returncode/stdout/stderr
# Must parse: ast.parse() succeeds
# Must sync: test functions match eval_manifest check IDs
```

Tasks that still fail quality gate → re-scaffold from scratch with improved prompts.

### Target

| Metric | Before | Target |
|--------|--------|--------|
| Total tasks | 283 | 283 |
| GOOD | 109 (38%) | 220+ (78%) |
| GOOD + OK | 134 (47%) | 260+ (92%) |

---

## History

### Phase 1: GLM-5.1 Setup (04-05)
- Z.AI Anthropic-compatible API works as drop-in
- Auth fallback chain: GLM → OAuth backup → Anthropic API key

### Phase 2: Config File Tiers (04-05)
- Tier 1 (agent instructions): CLAUDE.md, AGENTS.md, .claude/rules/, .claude/skills/, .cursorrules
- Tier 2 (docs): README.md, CONTRIBUTING.md — only with Tier 1

### Phase 3: Scouting (3 waves, 04-05)

| Wave | Repos | Raw | Filtered |
|------|-------|-----|----------|
| 1 (deep) | 12 | 182 | 108 |
| 2 (expanded) | 31 | 248 | 28 |
| 3 (wide) | 34 | 364 | 47 |
| **Total** | | **794** | **183** |

### Phase 4: Prompt Improvements (04-06)
- Skeleton-then-fill two-phase writing
- Gold reference files in `.claude/skills/scaffold-task/references/`
- Subprocess requirement in test-design.md
- 10 anti-pattern checklist
- Self-audit with syntax validation + source ref verification

### Quality Audits (04-05/06)

| Audit | n | GLM BAD% | Claude BAD% |
|-------|---|----------|-------------|
| Quick (batch) | 8 | 50% | 25% |
| Expanded | 30 | 57% | 25% |
| Deep (Opus, all anti-patterns) | 18 | 78% | 56% |
| Post-prompt-fix (today's scaffolds) | 76 | — | 23% WEAK |

## Auth Strategy

| Method | Cost | Limit | Best for |
|--------|------|-------|----------|
| GLM-5.1 | ~free | 5-hour cap (~40 tasks) | First pass |
| Claude OAuth | $0 (subscription) | Rate limited | Bulk reliable |
| Anthropic API | ~$6-10/task | Unlimited | Stragglers |

## GOOD Rate by Repo

| Repo | GOOD/Total | Rate |
|------|------------|------|
| unknown (old, no source_repo) | 97/218 | 44% |
| remix-run/remix | 3/8 | 37% |
| cloudflare/workerd | 2/5 | 40% |
| vercel/next.js | 2/6 | 33% |
| microsoft/playwright | 1/15 | 6% |
| dotnet/maui | 0/8 | 0% |
| biomejs/biome | 0/3 | 0% |

**Insight**: C#/Rust repos (maui, biome) are hardest — no easy subprocess pattern. Node repos respond well to `_run_ts()` helper.

## Files Changed (cumulative)

### Code
- `taskforge/config.py` — Tier 1/2 classification
- `taskforge/scout.py` — Tier-aware filtering, fetch cap
- `taskforge/pipeline.py` — backend_model tracking, `improve-tests` action
- `taskforge/prompts/scaffold_agentmd.md` — fixed origins, structural rules
- `taskforge/prompts/improve_tests.md` — **NEW** — upgrade grep→behavioral tests
- `taskforge/prompts/enrich_config_edit.md` — fixed origin examples
- `.claude/commands/scaffold-task.md` — expanded discovery, structural rules
- `.claude/skills/scaffold-task/test-design.md` — rewritten with examples
- `.claude/skills/scaffold-task/examples.md` — NEW, subprocess patterns
- `.claude/skills/scaffold-task/references/` — 4 gold reference files
- `scripts/run_scaffold_all.sh` — master pipeline with auth chain
- `scripts/rescaffold_and_audit.sh` — re-scaffold + cleanup pipeline

### Data
- `scouted_agentmd_prs_todo.jsonl` — 131 PRs
- `rescaffold_critical.jsonl` — 119 tasks re-scaffolded
- `rescaffold_oauth_retry.jsonl` — 78 tasks retried with OAuth
