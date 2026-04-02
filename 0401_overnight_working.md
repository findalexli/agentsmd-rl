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
- [x] Agent configs: 426/430 with full content in harbor_tasks/{task}/agent_configs.md

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
- 65 React, 45 VS Code, 1 Fiber — 0 overlap with harbor_tasks
- Convert each: pytest test_outputs.py + eval_manifest.yaml + standardized test.sh
- Delete old judge.py, judge_hook.sh, rubric.yaml
- Validate (nop=0, gold=1)
- Move passing tasks into harbor_tasks/

**Step 5: Scout fresh PRs** — DONE
- Used 49 repos in scouted_repos.jsonl
- ~100 new tasks created (339 → 439 total)
- Target: 400+ total validated tasks (harbor_tasks + converted kimi_drafts)

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
- [x] Copied 49 ready tasks to harbor_tasks/ (439 → 487)
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

### Remaining work
- [ ] Convert 62 partial kimi_drafts (need instruction.md generated)
- [ ] Regenerate corrupt patches (8 tasks) from PRs
- [ ] Debug E2B build failures — many may work with local Docker
- [ ] Git commit everything
- [ ] Update project memory
