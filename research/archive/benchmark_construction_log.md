# Overnight Working Log — 2026-04-01/02

## Goal
Remake all 430 harbor tasks with the new v2 format:
- pytest test_outputs.py (binary scoring)
- eval_manifest.yaml (replaces rubric.yaml)
- Improved quality across the board

## Progress Summary

### Phase 0: Setup — DONE
- [x] PR metadata: 430/430 tasks have PR numbers (task_metadata.jsonl)
- [x] Prompts: scaffold.md, validate.md, remake.md in taskforge/prompts/
- [x] Pipeline: `python -m taskforge.pipeline remake` works
- [x] Agent configs: 426/430 with full content in markdown_following/{task}/agent_configs.md

### Phase 1: Pilot — DONE
- [x] 3 tasks (python, node, rust): 3/3 remade + Docker validated (nop=0, gold=1)
- [x] Fixed test.sh template for non-Python base images

### Phase 2: First Remake (430 tasks) — DONE
- [x] 425/430 success, 5 timeouts retried OK → 430/430 remade

### Phase 3: Re-remake with Full Config Discovery — DONE
- [x] fetch_configs.py: discovers ALL config files at exact base commit
- [x] Handled GitHub API rate limits (5000/hr)
- [x] 425/430 success, 5 timeouts retried OK → 430/430 remade with full configs

### Phase 4: Docker Validation (local) — DONE
- [x] First pass: 156 pass (36%), 168 gold=0, 72 fail_build, 31 gold=missing

### Phase 5: Failure Analysis — DONE
All 3 investigations completed:

**fail_build (73 tasks):**
| Category | Count | Fix |
|----------|-------|-----|
| COPY files outside build context | 46 | Removed COPY lines (Harbor mounts at runtime) |
| GPG key expiry | 13 | Added apt-get clean before update |
| Disk false positives | 12 | No fix needed |
| Shallow clone | 6 | Changed --depth=N to --filter=blob:none |
| Missing unzip | 3 | Added to apt-get |
| Other (npm, cargo, Dockerfile) | 6 | Per-task |

**gold=0 (168 tasks):**
| Category | Count | Fix |
|----------|-------|-----|
| Wrong test assertions | 105 | Need per-task remake or deletion |
| Missing pip deps | 37 | Added torch-cpu/numpy/ruff/httpx/etc to Dockerfiles |
| Missing tools (ruff/ts) | 10 | Added to Dockerfiles |
| Cargo/Rust issues | 16 | Per-task |

**gold=missing (32 tasks):**
| Category | Count | Fix |
|----------|-------|-----|
| Corrupt patch (no trailing newline) | 21 | Batch sed fix on all 430 solve.sh |
| Patch doesn't apply (context mismatch) | 9 | Per-task |
| Other (merge conflict, truncated) | 2 | Per-task |

### Phase 6: Batch Fixes Applied
- [x] 438/439 Dockerfiles: removed invalid COPY lines (1 remains: openclaw-embeddings-http-write-scope)
- [ ] 0/427 Dockerfiles: GPG apt-get clean fix (NOT applied)
- [x] 129 Dockerfiles: added missing pip deps (torch-cpu, numpy, ruff, httpx, etc.)
- [x] 14 Dockerfiles: added ruff binary
- [x] 6 Dockerfiles: fixed shallow clone depth
- [x] 3 Dockerfiles: added unzip
- [x] 379 solve.sh: fixed trailing newline before PATCH delimiter
- [x] lint.py: added `lint_solve_sh()` with patch-trailing-newline, idempotency, heredoc checks

### Phase 7: E2B Re-validation — DONE
Using E2B sandboxes (~5x faster than local Docker):
- [x] E2B PoC validated (scripts/e2b_validate_batch.py)
- [x] Full validation completed: 430/430 processed
- [x] Results: 183 pass (42.6%), 142 invalid, 105 errors

### Phase 8: Systematic Fixes + Re-validate

**Step 1: Fix Dockerfile deps per repo** (~40% of failures)
- For each of 15 repos, identify what test_outputs.py imports and ensure Dockerfile installs it
- Common missing: torch-cpu, transformers, numpy, ruff, httpx, pydantic
- This is a batch fix across all tasks from that repo

**Step 2: Targeted re-remake** — PARTIALLY DONE
- 262 tasks attempted, 167 succeeded, 54 timeouts
- Filter: gold=0 tasks where deps ARE installed but test logic is wrong
- Re-run remake pipeline with improved prompt + full agent configs
- Skip tasks with dep issues (those are fixed in step 1)

**Step 3: E2B re-validate all** — RAN, RESULTS CORRUPTED
- Ran after steps 1+2, but results JSON corrupted
- Target: 300+ pass (70%+)

**Step 4: Convert kimi_drafts to v2** (111 tasks)
- All currently v1 format (old test.sh + rubric.yaml + judge.py)
- 65 React, 45 VS Code, 1 Fiber — 0 overlap with markdown_following
- Convert each: pytest test_outputs.py + eval_manifest.yaml + standardized test.sh
- Delete old judge.py, judge_hook.sh, rubric.yaml
- Validate (nop=0, gold=1)
- Move passing tasks into markdown_following/

**Step 5: Scout fresh PRs** — DONE
- Used 49 repos in scouted_repos.jsonl
- ~100 new tasks created (339 → 439 total)
- Target: 400+ total validated tasks (markdown_following + converted kimi_drafts)

---

## True Scoreboard (as of 2026-04-02 morning)

| Status | Count | Notes |
|--------|-------|-------|
| pass | 188 | 128 original + 60 fixed mislabels |
| fail_build | 111 | Docker build or setup failures |
| fail (gold=0) | 70 | Tests fail on gold patch |
| fail_gold (gold=0) | 50 | Tests fail on gold patch |
| error | 11 | Various |
| no status | 9 | Never validated |
| **Total** | **439** | |

---

## Phase 9: 8-Hour Execution (2026-04-02, 10am–6pm)

### Hour 1-2: Batch fix fail_build — DONE
- [x] COPY lines: 1 remaining fixed (openclaw-embeddings-http-write-scope)
- [x] apt-get GPG fix: 11 Dockerfiles fixed
- [x] Shallow clone: 19 fixed, unzip: 1, cargo edition: 2
- [x] E2B validate 111 fail_build → 37 now pass, 42 errors, 32 invalid
- [x] Retried 42 errors → 1 more pass, 41 persistent failures
- [x] Fixed validate_and_fix.sh verdict bug (regex "1.0" vs "1")
- Result: 226 passing (up from 188)

### Hour 2-4: Remake gold=0 tasks — DONE
- [x] 131 tasks queued for re-remake (106 gold=0 + 14 gold=missing + 11 error)
- [x] Sonnet remake: 110 OK, 21 timeouts
- [x] Opus retry of 21 timeouts: 21/21 OK
- [x] E2B validate 110 remade → 33 valid, 31 errors, 46 invalid
- [x] E2B validate 21 retried → 14 valid, 4 errors, 3 invalid
- Result: 263 → 284 passing

### Hour 4-5: Convert kimi_drafts — DONE
- [x] Triage: 49 ready, 62 partial, 0 broken
- [x] Copied 49 ready tasks to markdown_following/ (439 → 487)
- [x] Extracted source info (repo/commit) from 45 Dockerfiles → task.toml
- [x] Sonnet remake: 46/49 OK, 2 timeouts, 1 skipped
- [x] E2B validate 46 kimi + 21 retries → 25 valid, 21 errors, 21 invalid
- Result: 284 passing (11 kimi_drafts passed)

### Hour 5-6: E2B 404 fix + retry — DONE
- [x] Fixed E2B script to auto-rebuild stale templates on 404
- [x] Retried 44 sandbox-404 tasks → all 44 are real build failures (E2B can't build these Dockerfiles)
- Result: 284 passing (no change — these are persistent failures)

### Phase 9 Final Scoreboard (2026-04-02 14:10)

| Status | Count | % |
|--------|-------|---|
| **pass** | **284** | **58.3%** |
| fail | 99 | 20.3% |
| fail_build | 93 | 19.1% |
| no_status | 11 | 2.3% |
| **Total** | **487** | |

### Hour 6: Full E2B validation — DONE
- [x] Ran full E2B on all 487 tasks (clean run, fresh template builds)
- [x] 274 valid, 103 errors, 110 invalid, 669s runtime
- [x] Updated all 487 status.json

### Definitive Scoreboard (2026-04-02 14:30)

| Status | Count | % |
|--------|-------|---|
| **pass** | **274** | **56.3%** |
| fail (gold=0) | 109 | 22.4% |
| fail_build | 103 | 21.1% |
| fail_nop | 1 | 0.2% |
| **Total** | **487** | |

**Progress: 188 → 274 passing (+45.7%)**

### Remaining failure breakdown
- 76 Docker build failures (E2B can't build these Dockerfiles)
- 27 patch failures (solve.sh context mismatch or corrupt patch)
- 107 gold=0 (tests fail even with correct patch applied)
- 1 fail_nop (bun-ffi-linksymbols-nonobject-crash: nop=1,gold=1, useless)

### Hour 7: Wave 2 kimi_drafts + git commit — DONE
- [x] Generated instruction.md for 44 partial kimi_drafts (agent)
- [x] Copied 44 tasks to markdown_following (487 → 531)
- [x] Sonnet remake: 42/44 OK, 2 timeouts
- [x] E2B validate: 14 new passes
- [x] Git commit 1: da02a95 — V2 migration, 487 tasks, 274 passing
- [x] Git commit 2: 45e23d1 — 44 kimi_drafts, 288 passing

### Final Scoreboard (2026-04-02 15:40)

| Status | Count | % |
|--------|-------|---|
| **pass** | **288** | **54.2%** |
| fail | 122 | 23.0% |
| fail_build | 118 | 22.2% |
| fail_nop | 1 | 0.2% |
| no_status | 2 | 0.4% |
| **Total** | **531** | |

**Progress: 188 → 288 passing (+53%), 439 → 531 total tasks**

### Hour 8-10: Continued execution (2026-04-02 evening)
- [x] Regenerated 8 corrupt patches from PRs → 6 new passes (294 total)
- [x] Local Docker retry: 42 timeout tasks with 600s → 13 new passes (321)
- [x] E2B high-res (4 CPU, 4GB RAM) → 6 more passes on npm/bun tasks
- [x] Converted final 19 kimi_drafts (550 total tasks)
- [x] Remake wave 3: 166 tasks with opus/1200s → 148 OK, 18 FAIL
- [x] Git snapshot migration: 388 Dockerfiles → git init+fetch --depth=1 (faster builds, smaller .git)

### Current Scoreboard (2026-04-02 22:00)

| Status | Count | % |
|--------|-------|---|
| **pass** | **~340** | **~62%** |
| fail | ~120 | ~22% |
| fail_build | ~60 | ~11% |
| other | ~30 | ~5% |
| **Total** | **550** | |

**Progress: 188 → ~340 passing (+81%), 439 → 550 total tasks (+25%)**

### Hour 10-12: Overnight (2026-04-02 23:00 → 04-03 09:00)

**Completed:**
- [x] Full E2B validation post git migration → 394 passing (71.6%)
- [x] Rubric enrichment: 335 passing tasks reviewed for agent_config checks
  - v1 prompt (158 tasks): correct tests but some line number misattribution
  - v2 prompt (177 tasks): fixed line attribution + programmatic > rubric rule
  - ~53% of tasks got new checks, ~47% correctly had no relevant rules
- [x] Patch regeneration: 18 broken solve.sh regenerated with `git apply --3way`
- [x] Local Docker rust builds: 30 tasks with 900s timeout (in progress overnight)
- [x] All 111 kimi_drafts moved to markdown_following/ (550 total)

### Scoreboard (2026-04-03 09:00)

| Status | Count | % |
|--------|-------|---|
| **pass** | **394** | **71.6%** |
| fail | 74 | 13.5% |
| fail_build | 64 | 11.6% |
| no_status/other | 18 | 3.3% |
| **Total** | **550** | |

**Full session progress: 188 → 394 passing (+206, +110%), 439 → 550 tasks (+111)**

### Phase 10: Triage + cleanup (2026-04-03 09:00-09:30)
- [x] 10 parallel agents eyeballed all 138 failing tasks
- [x] Result: 65 salvageable, 73 delete
- [x] Deleted 58 low-quality tasks (43 + 15), 17 stuck with root-owned cache
- [x] Pass rate: 394 / 507 = 76.2%

### Phase 11: Salvage 65 remaining tasks (2026-04-03 in progress)

**Salvageable fail (gold=0) — 30 tasks:**
- Tests are close but have 1-2 assertion bugs, missing imports, or path issues
- Fix: targeted re-remake or manual fix per task

**Salvageable fail_build — 35 tasks:**
- Obvious Dockerfile fixes: missing yarn, apt retry, timeout increase, variable quoting
- 12 react tasks: all need `npm install -g yarn` added
- 8 ruff/uv tasks: apt-get exit 100 (transient) or already passing locally
- Fix: batch Dockerfile fixes + re-validate

### Target: 394 + ~40 salvaged = ~430+ passing

---

## Phase 12: AgentMD-Edits Dataset (2026-04-03, overnight + morning)

### Goal
Collect ~400 tasks where PRs update BOTH functional code AND agent config files (CLAUDE.md, AGENTS.md, README.md, SKILL.md, etc.). The idea: train/evaluate agents to make the right edits to those files alongside code changes.

### New requirement
Each task should test whether the agent:
1. Makes the correct code fix (binary, pytest)
2. Makes the correct config/documentation update (LLM-judged, rubric)

### Phase 12.1: Scouting — DONE
- Scouted 76 repos (49 existing + 27 new from GitHub code search)
- 500-1000 PRs per repo, 6-month lookback
- Filter: 2-15 files, 10-800 lines, both code + config changed
- **Bottleneck: only ~5% of PRs touch both code AND config files**
- Result: 242 candidate PRs after quality filter

**Quality filter pipeline:**
1. `scout_agentmd_prs.py` — heuristic: file patterns, size, date, labels
2. `filter_agentmd_prs.py` — fetch diffs, classify config edits, remove trivial
3. LLM scaffold filter — Claude skips unsuitable PRs (merge commits, config-only)

**Skip reasons the LLM caught that programmatic filters missed:**
- "chore: sync master" PRs (merge commits with incidental config changes)
- Config-only PRs disguised as code changes (just formatting/import reorder)
- PRs where config change is a version bump hidden in a large diff

### Phase 12.2: Batch Scaffold — DONE (5.7h, ~$1200)
- 242 PRs → 194 success, 48 LLM-skipped
- Opus model, $6/task budget, 4 workers, 900s timeout
- **0% budget exceeded, 0% timeout** — all failures are intentional skips

**Key finding: template placeholder leak**
The task template has a `test_config_rule()` with `NotImplementedError`. 80% of scaffolds left this placeholder instead of replacing it with real config tests. The LLM wrote real config tests elsewhere but didn't remove the placeholder.
- Fix: `fix_config_placeholders.py` removes them
- Fix: `relabel_config_checks.py` relabels config tests to `origin: config_edit`

### Phase 12.3: Architecture Decision — Config Tests → Rubric

**Problem discovered:** Gold patches contain byte-exact markdown diffs. An LLM agent would write semantically equivalent but differently worded content → binary test fails.

Analysis of 60+ config test functions:
| Pattern | % of tests | LLM pass rate |
|---------|-----------|---------------|
| Exact string match | 51% | 40-60% |
| Keyword AND | 25% | 65-75% |
| Keyword OR | 17% | 80-90% |
| Structural | 7% | 65-75% |

**Decision: Option A — move config edits to LLM-judged rubric**
- Binary reward = code tests only (pytest)
- Config edit quality = LLM judge, separate signal
- Gold patch stays complete (code + config)

**Implementation:**
1. `migrate_config_to_rubric.py` — moves `config_edit` checks from `checks[]` → `rubric[]`
2. Gold config diffs auto-extracted from solve.sh using `extract_config_hunks()` → stored in rubric `reference` field
3. `judge.py` updated — extracts agent's config hunks from their diff using same parser, compares side-by-side with gold reference semantically
4. `RubricRule` model updated with optional `reference: str` field

**Judge prompt (core question):**
> "Here's what the gold solution added to AGENTS.md. Here's what the agent added. Are they semantically equivalent?"

### Phase 12.4: Validation Results

**After migration (code-only binary):**

| Status | Count | % |
|--------|-------|---|
| pass | 95 | 33.8% |
| gold=0 (code tests) | 91 | 32.4% |
| build error | 22 | 7.8% |
| solve.sh error | 29 | 10.3% |
| other error | 44 | 15.7% |
| **Total** | **281** | |

**Why lower than initial 132?**
- 40 tasks had ALL tests as config tests → 0 tests after migration → config-only, should be excluded
- Remaining 196 tasks with code tests: 88 passing (44.9%)
- Some regressions from E2B template caching (stale templates with old test files)

### Phase 12.5: Pipeline Pitfalls Identified

**From claude -p research:**
1. **Not using `--bare`** — our pipeline loads CLAUDE.md, skills, hooks, auto-memory on every invocation. This wastes tokens (~1.3M cache reads/task) and can cause inconsistent behavior.
2. **No `--max-turns`** — if a scaffold loops, it burns budget silently.
3. **No `--no-session-persistence`** — each invocation saves a session, accumulating disk usage.
4. **Auto memory pollution** — 100+ runs on same repo pollute `MEMORY.md` with stale notes.
5. **Template placeholder not removed** — 80% of scaffolds left `NotImplementedError` placeholder.

**Recommended flags for batch operations:**
```bash
claude --bare -p "prompt" \
  --model opus \
  --max-budget-usd 6.0 \
  --max-turns 10 \
  --no-session-persistence \
  --allowedTools "Read,Edit,Bash,Write,Glob,Grep" \
  --output-format json
```

**From E2B validation analysis:**
- 49% of failures are "silent" (tests don't validate gold patch correctly)
- 24% are sandbox cache 404s (infrastructure, not task quality)
- 9% are stale patches in high-activity repos
- **No budget or timeout issues in scaffolding** (0% exceeded)

### Phase 12.6: Wave 2 Deep Scout — DONE
- 12 high-yield repos, 1000 PRs, 12 months → 46 new unique PRs
- 25 scaffolded, 21 LLM-skipped
- Total: 281 tasks (95 passing code-only binary)

### Current Scoreboard (2026-04-03 11:00)

**markdown_following (original):**
| Status | Count | % |
|--------|-------|---|
| pass | 394 | 71.6% |
| fail | 74 | 13.5% |
| fail_build | 64 | 11.6% |
| other | 18 | 3.3% |
| **Total** | **550** | |

**markdown_edits (new):**
| Status | Count | % |
|--------|-------|---|
| pass (code-only) | 95 | 33.8% |
| fail (code tests) | 91 | 32.4% |
| errors | 95 | 33.8% |
| **Total** | **281** | |
| rubric rules | 1223 | (428 with gold ref) |

### Lessons Learned

1. **PRs touching both code + config are rare (~5%)** — need very deep scouting (1000+ PRs/repo) or many repos
2. **LLM scaffold filter is valuable** — catches 24% of bad PRs that programmatic filters miss
3. **Exact string matching is unfair for NL output** — must use LLM judge for config edits
4. **Template placeholders leak** — always post-process to remove unfilled templates
5. **`claude -p` should use `--bare`** for batch ops — saves tokens, avoids auto-memory pollution
6. **Config-only tasks exist** — ~17% of agentmd PRs have no meaningful code change, just config updates. These need to be excluded or the task redefined.
7. **Same diff parser for gold and agent** — `extract_config_hunks()` applied to both ensures fair comparison

### Next Steps
- [ ] Fix 40 config-only tasks (add code tests or exclude)
- [ ] Fix 91 gold=0 tasks (re-scaffold with tighter prompt)
- [ ] Apply `--bare` flag to batch_scaffold_agentmd.py
- [ ] Target: 200+ passing agentmd tasks
- [ ] Investigate silent test failures (tests too permissive)
