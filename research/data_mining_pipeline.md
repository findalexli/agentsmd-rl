# Data Construction Methods

How we mine merged GitHub PRs and turn them into runnable benchmark tasks. Two corpora — *code-fix* and *markdown-authoring* — both released as Docker images on `ghcr.io/findalexli/agentsmd-rl/<task>:latest`.

**Snapshot 2026-04-27.**

| Corpus | Active | What "reward = 1" means | How tasks are built | Quality check |
|---|---:|---|---|---|
| `harbor_tasks/` | 582 | Agent reproduces the gold code fix | Claude Opus 4.7 in an isolated sandbox | Docker test (no fix → 0; gold → 1) + LLM rubric audit |
| `harbor_tasks_md_authoring/` | 718 | Agent's output contains the distinctive lines added by the gold patch | Deterministic script — no LLM | Two-stage Gemini 3.1 Pro judge |
| **Total** | **1,300** | | | |

## TL;DR

- **What we test**: whether an AI agent reads and follows a repo's *rule files* (`CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `.cursor/rules/*`) when modifying code.
- **Core assumption** *(§3)*: a PR is useful only when its gold fix is *shaped by* the rule files — i.e. the diff would look materially different if those files had been absent.
- **Where the volume goes**: 29,733 raw PRs → 9,629 candidates → 321 rule-file-only → 302 pre-judge → 214 newly built → ≈180 net new active tasks. **0.72 % per-PR yield, by design.**
- **Two pipelines split on what the diff modifies**. Pipeline A (Opus + sandbox) handles code; Pipeline B (deterministic verbatim-grep) handles rule-file-only PRs. Both end at ≈2 % yield, just via different filters.

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
| Latest scout | 2026-04-26, 12-month window, 147 repos | 2026-04-27, 24-month window, 1,037 repos |
| Cumulative active | **582** | **718** |

Pipeline B is for PRs whose transformation into a task is mechanical (extract distinctive added lines, grep for them in the agent's output). Routing such PRs through Pipeline A's Opus + sandbox produced lower-quality tasks because Opus occasionally invented additional files or paraphrased the diff, breaking the verbatim grep. The trade-off: Pipeline B's test is verbatim, so a competent agent that paraphrases the gold answer fails. The post-judge rejects PRs where this asymmetry is severe.

## 4. The funnel

Both pipelines lose ~99 % of their input to enforce the inclusion criterion. They differ in *where* the dominant cut lands. Bar widths below are proportional to share-of-raw.

### 4.1 Pipeline B — Markdown-authoring (2026-04-27 batch)

```
                                                                              %  of raw
29,733  ████████████████████████████████████████████████████████████████████  100.00  raw merged PRs from 1,037 repos
        │
        │  A2 — per-PR scout filters (size, labels, recency)        ×0.324    drops 67.6 %
        ▼
 9,629  ██████████████████████                                       32.39  candidates
        │
        │  A3 — rule-file-only path regex                            ×0.033    drops 96.7 %  ◄── DOMINANT CUT
        │      96.7 % mix code with markdown — routed to Pipeline A
        ▼
   321  ▊                                                             1.08  rule-file-only PRs
        │
        │  A4 — pre-judge title screen (Gemini, no patch)            ×0.941    drops  5.9 %
        ▼
   302  ▊                                                             1.02  scaffolder inputs
        │
        │  build script — 88 idempotent name-collisions
        │                  (already built in earlier scouts; skipped, not dropped)
        ▼
   214  ▌                                                             0.72  newly-built tasks
        │
        │  A4 — post-judge on merged 822-task corpus (Gemini, full patch)  ×~0.85   drops 12.7 %
        ▼
   ≈180  ▌                                                            ≈0.6   net new HIGH/MEDIUM tasks added
```

Per-PR new-task yield: **0.72 %**. Dominant cut: A3 — 96.7 % of candidates touch at least one non-rule-file path. Pipeline B's deterministic script is undefined on mixed code+markdown patches; those route to Pipeline A.

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
