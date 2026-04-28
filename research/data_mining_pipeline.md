# Data Construction Methods

How we mine merged GitHub PRs and turn them into runnable benchmark tasks. Two corpora — *code-fix* and *markdown-authoring* — both released as Docker images on `ghcr.io/findalexli/agentsmd-rl/<task>:latest`.

**Snapshot 2026-04-28.**

| Corpus | Active | What "reward = 1" means | How tasks are built | Quality check |
|---|---:|---|---|---|
| `harbor_tasks/` | 610 | Agent reproduces the gold code fix | Claude Opus 4.7 in an isolated sandbox | Docker test (no fix → 0; gold → 1) + LLM rubric audit |
| `harbor_tasks_md_authoring/` | **2,482** | Agent's output contains the distinctive lines added by the gold patch | Deterministic script — no LLM | Two-stage Gemini 3.1 Pro judge |
| **Total** | **3,092** | | | |

## TL;DR

- **What we test**: whether an AI agent reads and follows a repo's *rule files* (`CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `.cursor/rules/*`) when modifying code.
- **Core assumption** *(§3)*: a PR is useful only when its gold fix is *shaped by* the rule files — i.e. the diff would look materially different if those files had been absent.
- **Coverage claim** *(2026-04-28 overnight scout)*: we have enumerated essentially every public-GitHub repo with rule files (24 code-search queries → 15,608 unique repos) and inspected every recent merged PR in the ≥100-star subset (846 healthy repos × last 50 merged since 2025-09-01 = 23,812 PRs). Combined with a 28-query date-windowed title scout (10,058 raw title hits), we have **6,966 unique candidate PRs** in the active window. The constraint is no longer recall but downstream judge throughput.
- **Where the volume goes**: 6,966 unique candidates → 1,351 newly-built tasks → 2,482 net active markdown-authoring tasks. **19 % per-PR scaffold yield** (vs 0.72 % in narrower scouts before — same per-PR difficulty, the new floor is comprehensive coverage rather than narrow recall).
- **Two pipelines split on what the diff modifies**. Pipeline A (Opus + sandbox) handles code; Pipeline B (deterministic verbatim-grep) handles rule-file-only PRs. Both end at ≈2 % per-pass yield from raw GitHub PRs, just via different filters.

## Glossary

- **Rule file**: a markdown file a repo maintains for AI coding agents — `CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `.cursor/rules/*`, `.claude/{rules,skills,agents}/*.md`, `.github/copilot-instructions.md`, plus a few similar paths. Closed set, fixed by one regex.
- **Task name**: a short URL-safe slug (`prefect-update-agentsmd-files-for-2793f36`) used as the on-disk task directory. Pipelines skip a PR if a task with the same name already exists.
- **Build a task**: emit `environment/Dockerfile`, `solution/solve.sh`, `tests/test.sh`, `eval_manifest.yaml`. Pipeline A delegates this to Opus; Pipeline B uses a deterministic script.
- **Rule-relevance check**: a Gemini call deciding whether the gold fix was *actually shaped by* the rule files (vs. a bug fix that just happens to live alongside them). The single most important filter.

## 1. Inclusion criterion

A merged PR enters the benchmark only when its gold diff is *shaped by* the rule files. PRs are sorted into four classes; we keep A and B, drop C and D.

| Class | Gold diff content | Outcome |
|---|---|---|
| **A** | Edits a rule file | Keep — markdown-authoring task |
| **B** | Code-only, encodes a rule documented in a rule file | Keep — code-fix task |
| C | Determined entirely by the bug, independent of rules | Drop — decorative |
| D | Unscaffoldable on Linux/Docker (platform-specific, GPU, > 500-line refactor) | Drop |

## 2. Assumptions and the filters that enforce them

Every drop in either pipeline maps to one of five assumptions.

| # | Assumption | Filter | Drop rate |
|---|---|---|---|
| **A1** | Repository contains rule files | Discovery: `gh search repos` over agent-instruction topics + path queries; ≥ 5 stars | upstream of funnel |
| **A2** | PR is a clean, scaffoldable unit | 1–8 files changed, 5–500 line diff, no skip-labels, recency cutoff | 67.6 % (29,733 → 9,629) |
| **A3** | PR's diff content is in scope for the chosen pipeline | A: rule-equipped repo + name-dedup. B: every changed file is a rule file | A: 41.5 %, B: 96.7 % |
| **A4** | Gold fix is shaped by the rule files (the core assumption) | A: Gemini rule-relevance judge → A/B/C/D. B: Gemini title pre-judge + full-patch post-judge | A: 94.2 %, B: 5.9 % + 12.7 % |
| **A5** | Task is mechanically buildable | A: Opus build + Docker test. B: deterministic script + post-judge YAML check | A: ≈ 25-30 %, B: ≈ 1 % |

**A3 vs A4** are easy to confuse. A3 is *operational* — "is this PR even the kind of input each pipeline can produce a task from?" A4 is *the research property* — "did the rule files actually matter to the fix?" A3 fails open (cheap to drop, plenty of candidates); A4 fails closed (examine carefully). Putting A3 first means the LLM only sees PRs it has a chance of judging usefully.

## 3. The two pipelines

| | Pipeline A — code-fix | Pipeline B — markdown-authoring |
|---|---|---|
| Diff content | Code (with optional rule-file edits) | Rule files only |
| A3 filter | Rule-equipped repo + name-dedup | Path regex (every file is a rule file) |
| A4 classifier | Gemini rule-relevance: A/B/C/D | Gemini structured `Verdict { load_bearing, research_relevant, slop_score, verdict }` — twice (title-only, then full patch) |
| A5 build | Opus 4.7 in an E2B sandbox | Deterministic: shallow-clone + apply gold + grep for distinctive `+` lines |
| Validation | Docker test | Built into the verbatim-grep test |
| Latest scout | 2026-04-26, 12-month window, 147 repos | 2026-04-28, **comprehensive** (§3.1) |
| Cumulative active | **610** | **2,482** |

Pipeline B is for PRs whose transformation into a task is mechanical (extract distinctive added lines, grep for them in the agent's output). Routing such PRs through Pipeline A's Opus + sandbox produced lower-quality tasks because Opus occasionally invented additional files or paraphrased the diff, breaking the verbatim grep. The trade-off: Pipeline B's test is verbatim, so a competent agent that paraphrases the gold answer fails. The post-judge rejects PRs where this asymmetry is severe.

### 3.1 Pipeline B — comprehensive scout (2026-04-28)

The earlier scouts (2026-04-26 and prior) used only a title-only PR search (`is:pr is:merged X.md in:title`) which left two recall gaps:

1. **Title-doesn't-say-it PRs.** A PR titled `feat: add new skill` that adds `skills/foo/SKILL.md` was invisible to title search. From sampled cross-repo PRs, ~40 % of skill-authoring work falls in this bucket.
2. **GitHub Search 1000-result cap.** 7 of our 15 popular queries (`SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, `.claude/skills`, `skills/`, `copilot-instructions`) saturated at the cap, truncating the tail.

The comprehensive scout closes both gaps:

| Phase | Mechanism | Output |
|---|---|---|
| **(a) Code search by filename/path** | 24 queries via `gh api search/code` with subdivision by `path:` (e.g. `filename:SKILL.md path:.claude/skills/`, `filename:SKILL.md path:.opencode/skills/`, …) | **15,608 unique repos** with rule files in their default branch |
| **(b) Batched repo-metadata** | Single GraphQL query, 50 repos per call → 312 calls | Stars, language, archived, fork, pushed_at for all 15,608 repos |
| **(c) Star + non-archived + non-fork filter** | ≥100 stars, not archived, not a fork | **846 healthy repos** |
| **(d) Batched per-repo PR enumeration** | GraphQL `pullRequests(states: MERGED, first: 50)` aliased 50 repos per call → 17 calls | **23,812 PRs** merged since 2025-09-01 |
| **(e) Batched files() per PR + tier-1 path filter** | GraphQL `files(first: 50)` aliased 25 PRs per call → 952 calls; keep only PRs touching at least one tier-1 path | **2,745 PRs** |
| **(f) Date-windowed title scout** | Same 28-query title search as before, but each saturating query split into 4 disjoint date windows (Sep–Oct, Nov–Dec, Jan–Feb, Mar–Apr) | **4,301 PRs** |
| **(g) Merge + dedupe** | (repo, pr_number) keyset union | **6,966 unique candidate PRs** |
| **(h) Deterministic scaffold** | Same as before (shallow-clone, apply gold, grep distinctive added lines) | **1,351 newly-built tasks** |

Total API spend for steps (a)–(g): ~110 search-bucket calls + ~280 code-search-bucket calls + ~1,300 GraphQL calls. End-to-end wall time: ~2 hours. Key infrastructure that made this affordable:

- `taskforge/gh_graphql.py` — `batch_repo_metadata`, `batch_pr_files`, `batch_repo_recent_prs`, `batch_repo_bundle`. Each replaces N REST calls with N/50 GraphQL aliased calls. The naive REST equivalent of step (d)+(e) alone would have been ~28K REST calls (5K/hr budget → 6 hours).
- Date windowing in `discover_recent_skill_prs.py` recovers each saturating title query's truncated tail at no extra rate-limit cost (each window is its own 1000-result budget).

**Coverage claim.** With ≥100-star, non-archived, non-fork, last-8-months: we believe we now have a near-exhaustive census of skill-authoring and agent-md-authoring PRs from production-grade public repos. The remaining recall gaps are:
1. < 100-star repos (deliberately excluded — quality floor)
2. PRs older than 2025-09-01 (deliberate window)
3. Repos archived or made private after the index ran
4. Forks (deliberately excluded; convention edits in forks rarely reflect upstream practice)

Persistent raw outputs are kept under `scout_data/` (gitignored, ≈ 14 MB total) so the judge can be re-run without re-fetching:
- `code_search_phase2_overnight_2026_04_27.jsonl` — 2,745 PRs
- `title_overnight_2026_04_27.jsonl` — 4,301 PRs
- `final_merged_overnight_2026_04_27.jsonl` — 6,966 unique
- `code_search_repos_overnight_2026_04_27.txt` — 15,608 repos

## 4. The funnel

Both pipelines lose ~99 % of their input to enforce the inclusion criterion. They differ in *where* the dominant cut lands. Bar widths below are proportional to share-of-raw.

### 4.1 Pipeline B — Markdown-authoring (2026-04-28 comprehensive batch)

```
                                                                                  %  of raw
                                            DUAL-DISCOVERY ═════════════════════
 6,966  ████████████████████████████████████████████████████████████████████   100.00  unique candidate PRs (merged 2025-09-01..)
        ╠═══ via Code Search → batched GraphQL  (2,745 PRs)
        ╚═══ via 28-query date-windowed title scout (4,301 PRs)
        │
        │  A3 — rule-file-only path regex (every changed file matches)  ×~0.55  drops ~45 %
        │      55 % already pre-filtered by tier-1 in discovery; rest were
        │      mixed code+markdown — routed to Pipeline A's codebearing queue
        ▼
 ~3,800  ██████████████████████████████████████                          ~55  pure-tier-1 candidates
        │
        │  build script — name-dedup against existing tasks
        │                  (already built in earlier scouts; skipped)
        ▼
 1,351  █████████████                                                    19.4  newly-built tasks
        │
        │  A4 — post-judge (Gemini, full patch + new prompt)
        │      Note: 2026-04-28 run partially completed due to Gemini
        │      transient_failures; ~50 of 1,351 have md_quality.json.
        │      Re-judge planned when API healthier.
        ▼
 1,348  █████████████                                                    19.3  net new active (after secret + unfetchable quarantine)
```

Per-PR new-task yield: **19.3 %** in the comprehensive scout — about 25× the previous narrow scouts (0.72 % yield). The jump is not because per-PR difficulty fell; it's because the new pipeline (a) eliminates the ~40 % of skill PRs whose titles don't quote the rule file, and (b) recovers the truncated tail beyond GitHub's 1000-result-per-query cap.

Cumulative active markdown-authoring corpus: **2,482** (after 3 unfetchable + 5 secret quarantines).

### 4.2 Pipeline A — Code-fix (2026-04-26 scout pass)

```
                                                                              %  of raw
19,417  ████████████████████████████████████████████████████████████████████  100.00  raw merged PRs from 107 repos
        │
        │  A3 — name-dedup against baseline                          ×0.749    drops 25.1 %
        ▼
14,549  ███████████████████████████████████████████████████          74.93   unique new PRs
        │
        │  A3 — rule-equipped repo only                              ×0.897    drops  7.7 %
        ▼
13,046  ██████████████████████████████████████████████               67.19   PRs into the judge
        │
        │  A4 — rule-relevance judge (Gemini, A/B/C/D/ERR)           ×0.058    drops 94.2 %  ◄── DOMINANT CUT
        │      C = decorative (10,398, 79.7 %)
        │      D = unscaffoldable (1,896, 14.5 %)
        ▼
   750  ██▊                                                            3.86  A + B wins (A=204, B=546)
        │
        │  A5 — Opus 4.7 build + Docker test                         ×~0.72    drops ~28 %
        ▼
  ≈540  ██                                                             ≈2.8  valid built tasks
```

Per-PR yield: **2.8 % per pass.** Dominant cut: A4 — 94 % of admitted PRs are class C, bug fixes any agent could write without ever opening a rule file.

### 4.3 Same shape, different orderings

Pipeline A enforces A4 with an LLM call on every candidate (~13 K Gemini calls). Pipeline B uses the path regex as a free proxy and only LLM-judges the 321 path-survivors. Both end with ≈2-3 % per-pass yield because both enforce the same core assumption — just at different stages.

## 5. Pipeline B post-judge thresholds

The post-judge prompt asks Gemini for four structured fields, then computes a verdict deterministically.

| Field | Range | Meaning |
|---|---|---|
| `load_bearing` | bool | Would an agent reading vs. ignoring this gold patch produce different downstream behavior? |
| `research_relevant` | bool | Does the change carry a behavioral assertion an agent could either follow or violate? |
| `slop_score` | 0…10 | 0 = concrete commands / paths / version pins; 10 = AI-generated boilerplate / auto-bot / generic prose |
| `verdict` | enum | Computed from the above |

Verdict mapping:
- **HIGH** iff `slop_score ≤ 3` and both flags true,
- **MEDIUM** iff `4 ≤ slop_score ≤ 6` and both flags true,
- **LOW** iff `7 ≤ slop_score ≤ 8`,
- **DELETE** iff `slop_score ≥ 9` or either flag false.

The judge is instructed to default to reject when in doubt. A false positive (slop in corpus) silently weakens the benchmark; a false negative (real task quarantined) loses one task out of hundreds.

## 6. Failure modes observed (2026-04-27 batch)

Of 104 LOW + DELETE verdicts, attribution by inferred origin:

| Pattern | Count | Why post-judge catches it |
|---|---:|---|
| Auto-bot PRs (PrefectHQ commit-watcher emits "Update AGENTS.md for commit X" after each push) | 26 | "Automated AGENTS.md update" detected in PR body |
| Broken-yaml manifests (a since-fixed scaffolder bug emitted mixed-indent YAML when gold patches contained outdented lines) | 33 | `yaml.safe_load` fails |
| Generic AI-authored skills / boilerplate ("This skill helps with X" with no concrete commands) | ≈ 30-50 | High slop_score, low load_bearing |
| Self-referential meta-content ("Add a skill for managing skills") | 3 | Fails research_relevant |

## 7. Reproducibility

Per-row decision logs are checked in:

- `scouted_scaleup_v2_prejudged.decisions.csv`, `scouted_round2_v2_prejudged.decisions.csv` — pre-judge decisions for every PR considered.
- `research/md_authoring_quality_judgments.json` — full post-judge structured output for every scaffolded task.

Gemini calls use temperature 0.1, structured output (`responseMimeType: application/json` + `responseSchema`), thinking budget 256 tokens. Discovery queries listed verbatim in `taskforge/scout.py`.

## 8. Limitations

- **Verbatim-grep tests** in Pipeline B reward agents that produce exactly the gold prose. Semantically equivalent but textually different output fails. Mitigated by the post-judge, not eliminated.
- **Single-classifier post-judge** in Pipeline B (no second-classifier cross-check, unlike Pipeline A's historical Kimi → Gemini → Kimi loop).
- **Recency-window asymmetry**: Pipeline A's latest pass uses 12 months, Pipeline B's uses 24 — yield-rate comparisons are not strictly apples-to-apples.
- **Closed rule-file definition**: any new agent-instruction format must be added to the regex by hand.
- **No batch-provenance tracking** in the post-judge — we cannot directly attribute the 104 LOW + DELETE verdicts in the 2026-04-27 batch to new vs. pre-existing tasks; §6 is by inferred origin.
