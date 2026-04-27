# Data Construction Methods

This document explains how we mine merged GitHub PRs and turn them into runnable benchmark tasks. The protocol produces two corpora — *code-fix tasks* and *markdown-authoring tasks* — both released as pre-built Docker images on `ghcr.io/findalexli/agentsmd-rl/<task>:latest`.

**Corpus snapshot (2026-04-27).**

| Corpus | Active | What "reward = 1" means | How each task is built | Quality check |
|---|---:|---|---|---|
| `harbor_tasks/` | 582 | The agent reproduces the gold code fix | Claude Opus 4.7 reads the repo and writes the task, in an isolated sandbox | Docker test (build → fail without fix → pass with fix) + LLM rubric audit |
| `harbor_tasks_md_authoring/` | 718 | The agent's output contains the distinctive lines added by the gold patch | A short script copies the patch into a verbatim grep test — no LLM | Two-stage Gemini 3.1 Pro judge |
| **Total** | **1,300** | | | |

---

## How to read this document

A few terms recur. We define each one once here in plain English; the rest of the document uses them as shorthand.

- **Rule file** *(sometimes labeled "tier-1 instruction file")*: a markdown file a repository maintains so AI coding agents can read it before changing code — `CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `.cursor/rules/*`, and similar. The exact list is fixed in §3.
- **Slug**: a short, URL-safe name we generate per PR (e.g. `prefect-update-agentsmd-files-for-2793f36`) and use as the on-disk task directory. "Skip on slug" means: don't process a PR if a task with the same slug already exists in the corpus.
- **Build a task** *(sometimes labeled "scaffold")*: produce the four files Harbor needs to run the task — `environment/Dockerfile`, `solution/solve.sh` (applies the gold fix), `tests/test.sh` (returns 0 or 1), `eval_manifest.yaml` (declarative spec of what the agent should achieve). Pipeline A uses Opus to do this; Pipeline B uses a deterministic script.
- **Rule-relevance check** *(sometimes labeled "causality judge")*: a Gemini call that decides whether the gold fix was *actually shaped by* the repo's rule files — vs. being a bug fix that just happens to live in a repo with rule files. This is the most important filter in either pipeline.

Where we use a technical label as a filter name (e.g. "tier-1 path regex"), we keep it consistent across §4-§9 so the funnel diagrams in §9 line up with the assumptions in §4.

---

## 1. What this benchmark tests

Whether an AI coding agent reads and follows the rule files a repository maintains, when modifying code or writing new rules.

The hard part is constructing tasks where the *correct* answer is genuinely shaped by what the rule files say. A task whose gold solution would be identical even if the rule files vanished is useless: an agent that ignores the rules can still pass it. Every benchmark task we keep must carry a clean signal that *something in the rule files mattered to the fix*.

## 2. Core assumption

> **A merged PR is a useful benchmark task only when its gold diff is shaped by the rule files — i.e., the diff would look materially different if the rule files had been absent.**

Every filter in the pipeline exists to enforce this one assumption. PRs that fail it produce tasks where reward is uninformative about instruction-following.

## 3. Definitions

**Rule file.** A file matching the regex below. We treat this as a closed set; any new agent-instruction format must be added to the regex by hand before the pipeline recognizes it.

> `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `CONVENTIONS.md`, `SKILL.md`, `.cursorrules`, `.windsurfrules`, `.clinerules`, `.continuerules`, `*.mdc`, `.claude/{rules,skills,agents}/*.md`, `.cursor/rules/*`, `.github/copilot-instructions.md`, `.github/skills/*/SKILL.md`, `.github/prompts/*.prompt.md`, `.{agents,opencode,codex}/skills/*/SKILL.md`.

A repository is **rule-equipped** if it contains at least one rule file.

**PR class.** Every PR we judge for rule-relevance falls into one of four classes:

| Class | The gold diff... | Outcome |
|---|---|---|
| **A** | edits a rule file | Keep — markdown-authoring task |
| **B** | is code-only, but the code change encodes a specific rule from a rule file | Keep — code-fix task |
| **C** | is determined entirely by the bug, independent of any rule | Drop — decorative |
| **D** | cannot be turned into a Linux Docker benchmark (platform-specific runtime, GPU, multi-thousand-line refactor, no testable behavior) | Drop — unscaffoldable |

**Docker test.** An automated check on a freshly-built task image. It asserts (a) running with the *base* commit (no fix applied) gives reward = 0, and (b) running after the *gold patch* gives reward = 1. Tasks that fail either assertion are quarantined.

## 4. The five assumptions and the filters that enforce each

Every drop in the pipeline maps to one of five assumptions. Below: the assumption in plain English, the filter that enforces it, and the empirical drop rate observed on the 2026-04-27 batch.

| # | Assumption | Filter | Drop rate (this batch) |
|---|---|---|---|
| **A1** | The repository contains rule files | Repository discovery: `gh search repos` over agent-instruction-related topics + path queries; require ≥ 5 stars | upstream of the funnel (governs which repos we even scout) |
| **A2** | The PR is a clean, scaffoldable unit of work | Per-PR scout filters: 1–8 files changed, 5–500 total lines added+deleted, no `wontfix`/`dependencies`/`automated-update` labels, within recency window | 67.6 % (29,733 → 9,629) |
| **A3** | The PR's diff content is in scope for the chosen pipeline | Pipeline A: only PRs from rule-equipped repos, with name-based dedup against the existing corpus. Pipeline B: every changed file must be a rule file | A: 41.5 % (slug-dedup + repo allowlist together); B: 96.7 % (path regex) |
| **A4** | The gold fix is shaped by the rule files (the core assumption from §2) | Pipeline A: a Gemini rule-relevance check that classifies each PR as A / B / C / D / ERR. Pipeline B: a Gemini check on the title before building the task, then a stricter Gemini check on the gold patch after | A: 94.2 % drop at the rule-relevance check; B: 5.9 % at the title-level pre-check + 12.7 % at the post-check |
| **A5** | The task is mechanically buildable into a runnable Docker test | Pipeline A: Opus builds the task in an E2B sandbox; the Docker test must pass. Pipeline B: deterministic script with idempotency check; manifests that fail YAML parsing are rejected by the post-judge | A: ≈ 25–30 % build-fail; B: ≈ 1 % build-fail |

The pipelines split on **A3**. Pipeline A admits any code-bearing PR from a rule-equipped repo and then leans on the rule-relevance check (A4) to decide what's worth building. Pipeline B starts strict on A3 — every file must be a rule file — so the LLM judges in A4 are smaller and cheaper. PRs that A3 drops in Pipeline B are not lost; they are routed to a side queue (`*_codebearing.jsonl`, 34,358 cumulative rows) for later processing through Pipeline A.

## 5. The two pipelines at a glance

| | Pipeline A — code-fix | Pipeline B — markdown-authoring |
|---|---|---|
| What's in the gold diff | Code (optionally with rule-file edits) | Rule files only |
| Pre-classifier filter (A3) | Rule-equipped *repo* + name-based dedup | Every changed file is a rule file |
| Classifier (A4) | Gemini rule-relevance: A/B/C/D/ERR | Gemini structured judge: HIGH/MEDIUM/LOW/DELETE — twice (title-only, then full patch) |
| Task build (A5) | Opus 4.7 in an E2B sandbox | Deterministic script: shallow-clone, copy the gold patch into a grep-based test |
| Validation | Docker test | Built into the verbatim-grep test |
| Latest scout window | 12 months | 24 months |
| Latest scout repos | 147 | 1,037 |
| Cumulative active tasks | 582 | 718 |

## 6. Discovery and scout (shared by both pipelines)

**Discovery — finding rule-equipped repos.** We search GitHub for repositories that maintain rule files. Concretely: `gh search repos` over thirteen agent-instruction-related topics and three repository-path queries.

> Topics: `claude-code`, `claude-skills`, `claude-agents`, `agent-skills`, `agents-md`, `claude-md`, `cursor-rules`, `awesome-skills`, `awesome-claude-code`, `claude-plugins`, `claude-code-skill`, `agent-instructions`, `llm-rules`.
> Paths: `SKILL.md in:path`, `.claude/skills in:path`, `.cursor/rules in:path`.

For each query we sort by stars, take the top 200–300 results, keep only repositories with at least 5 stars (excludes empty/abandoned projects), and deduplicate against repos we scouted earlier.

**Scout — fetching merged PRs.** For each retained repository we ask GitHub for up to 200 recent merged PRs in JSON form, including the *file paths* each PR changed:

```
gh pr list --state merged --limit 200 \
   --json number,title,changedFiles,additions,deletions,mergedAt,labels,mergeCommit,files
```

(Above 200, GitHub's GraphQL endpoint returns 504 on large repositories.) Including `files` at scout time gives us each PR's path list and avoids ≈ 50× of follow-up REST `/files` calls in Pipeline B's downstream filtering.

The **per-PR scout filters** apply assumption A2: skip PRs that change > 8 files, add+remove > 500 lines or < 5, carry one of the skip-labels (`wontfix`, `dependencies`, `automated-update`, `no-changelog`), or merged before the recency cutoff. There is one exemption: a PR that changes only docs is normally dropped at this stage, but if every changed file is a rule file we keep it (these are the inputs Pipeline B will eventually scaffold).

| Pipeline | Repos scouted | Raw merged PRs fetched | After A2 filters |
|---|---:|---:|---:|
| A — Code-fix (2026-04-26 pass) | 107 | 19,417 | 14,549 |
| B — Markdown-authoring (2026-04-27 batch) | 1,037 | 29,733 | 9,629 |

## 7. Pipeline A — Code-fix tasks

Numbers below are for the 2026-04-26 scout pass. The cumulative `harbor_tasks/` corpus is the result of multiple such passes accumulated over weeks.

| Stage | Filter | Enforces | In | Drop | Out |
|---|---|---|---:|---:|---:|
| 7.1 Skip on slug | A PR is dropped if a task with its slug already lives in the corpus (avoids redoing work) | A3 | 19,417 | 4,868 | 14,549 |
| 7.2 Rule-equipped repo only | Drop PRs from repos with no rule file | A3 | 14,549 | 1,503 | 13,046 |
| 7.3 Rule-relevance check | Gemini 3.1 Pro classifies each PR as A / B / C / D / ERR | A4 | 13,046 | 12,294 | 750 (A=204, B=546) |
| 7.4 Build task + Docker test | Opus 4.7 inside an E2B sandbox: clone repo, apply gold, write the test, then Docker-test it (no fix → 0; gold → 1) | A5 | 750 | ≈ 25–30 % | ≈ 530–560 |
| 7.5 Quality audit | LLM rubric audit; tier-A/B failures are quarantined | A5 | ≈ 540 | small | merged into corpus |

**Cumulative**: 582 active tasks in `harbor_tasks/`, 92.8 % Docker-test pass rate (540 pass / 41 fail / 1 missing). End-to-end yield this pass: ≈ 540 / 19,417 ≈ **2.8 %**.

The dominant cut is **7.3, the rule-relevance check.** Without it, ≈ 94 % of admitted PRs are class C — fixes that have nothing to do with the rule files. A benchmark built from those would be silent on instruction-following, exactly the failure mode §2 forbids.

## 8. Pipeline B — Markdown-authoring tasks

Pipeline B targets PRs that *only* edit rule files. The transformation from such a PR to a runnable benchmark task is mechanical: extract the most distinctive added lines from the gold patch, then write a test that asserts those lines appear in the agent's output. We replace Pipeline A's per-task Opus call with a deterministic script, and add two Gemini quality gates around it — a cheap title-level check before the script runs, and a stricter full-context check after.

### 8.1 New-candidate pipeline (chains 9,629 → 214)

| Stage | Filter | Enforces | In | Drop | Out |
|---|---|---|---:|---:|---:|
| 8.1.1 Rule-file-only path regex | Every changed file in the PR must match the rule-file regex. PRs with any non-rule-file path go to a side queue (`*_codebearing.jsonl`, 34,358 cumulative rows across all 2026-04 scouts) for later Pipeline A processing — they are not lost, just deferred | A3 | 9,629 | 9,308 | **321** |
| 8.1.2 Pre-judge (title-only) | Gemini 3.1 Pro Standard, given only `{repo, title, file_paths}` (no PR body, no patch). Drops bot-generated titles, dummy-test PRs, version-bump-only titles, generic boilerplate. Conservative — defaults to KEEP | A4 | 321 | 19 | 302 |
| 8.1.3 Build task (deterministic) | Shallow-clone the repo at the base commit (`git fetch --depth=1 origin <SHA>`); generate `Dockerfile`, `solve.sh` (applies the gold patch verbatim), `tests/test_outputs.py` (3 pytest assertions, one per distinctive added line — longest `+` lines, ≥ 12 chars, alphanumeric, deduplicated), and `eval_manifest.yaml` v2.0. No LLM call | A5 | 302 | 88 (slug already in corpus) | **214 newly built** |

### 8.2 Corpus re-validation (independent count, 822 → 718)

After §8.1 we have 214 new tasks plus 608 tasks already in `harbor_tasks_md_authoring/` from earlier scouts — 822 in total. The post-judge re-validates *all 822*, not just the new ones, so it can clean up legacy tasks at the same time.

| Stage | Filter | Enforces | In | Drop | Out |
|---|---|---|---:|---:|---:|
| 8.2.1 Post-judge (full context) | Gemini 3.1 Pro Standard, given `instruction.md` + the complete gold patch. Returns a structured `Verdict { load_bearing, research_relevant, slop_score, evidence, verdict ∈ {HIGH, MEDIUM, LOW, DELETE} }`. Verdict thresholds in §10 | A4 | 822 | 104 | 706 HIGH + 12 MEDIUM |
| 8.2.2 Quarantine | Move LOW + DELETE to `harbor_tasks_md_authoring_quarantine_quality/`. Each quarantined task keeps its `md_quality.json` as an audit trail | — | 104 | — | **718 active** |

Cumulative active yield: 718 / 9,629 ≈ **7.5 %**. Per-batch new-task yield: 214 / 9,629 ≈ **2.2 %**.

## 9. The funnel — where every PR goes

Both pipelines end at similar yields (Pipeline A ≈ 2.8 %, Pipeline B ≈ 2.2 % per pass). What differs is *where* the volume is lost. The waterfalls below show each pipeline's per-stage drop. **Bar widths are proportional to share-of-raw**; the dominant drop in each pipeline is tagged.

### 9.1 Pipeline B — Markdown-authoring (2026-04-27 batch)

```
                                                                              %  of raw
29,733  ████████████████████████████████████████████████████████████████████  100.00  raw merged PRs from 1,037 repos
        │
        │  A2 — per-PR scout filters (size, labels, recency)        ×0.324    drops 67.6 %
        ▼
 9,629  ██████████████████████                                       32.39  candidates
        │
        │  A3 — rule-file-only path regex                            ×0.033    drops 96.7 %  ◄── DOMINANT CUT
        │      (the other 96.7 % mix code with markdown and route
        │       to Pipeline A's side queue, not lost)
        ▼
   321  ▊                                                             1.08  rule-file-only PRs
        │
        │  A4 — pre-judge title screen (Gemini, no patch context)    ×0.941    drops  5.9 %
        ▼
   302  ▊                                                             1.02  candidates the build script will see
        │
        │  build script: 88 idempotent slug-collisions
        │                (those PRs were already built in
        │                earlier scouts — skipped, not dropped)
        ▼
   214  ▌                                                             0.72  newly-built task directories
        │
        │  A4 — post-judge on the merged 822-task corpus             ×~0.85    drops 12.7 %
        │       (Gemini sees the complete gold patch).
        │       The new-task share of these drops is unattributed
        │       — see Limitations (§14).
        ▼
   ≈180  ▌                                                            ≈0.6   net new HIGH/MEDIUM tasks added by this batch
```

**Per-PR new-task yield: 0.72 %.** The dominant cut is **A3** (the rule-file-only regex): 96.7 % of candidates touch at least one non-rule-file path. This is structural — Pipeline B's deterministic script only works on patches that are 100 % rule files. Anything mixed routes to Pipeline A.

### 9.2 Pipeline A — Code-fix (2026-04-26 scout pass)

```
                                                                              %  of raw
19,417  ████████████████████████████████████████████████████████████████████  100.00  raw merged PRs from 107 repos
        │
        │  A3 — skip on slug (already in baseline corpus)            ×0.749    drops 25.1 %
        ▼
14,549  ███████████████████████████████████████████████████          74.93   unique new PRs
        │
        │  A3 — rule-equipped repo only                              ×0.897    drops  7.7 %
        ▼
13,046  ██████████████████████████████████████████████               67.19   PRs into the judge
        │
        │  A4 — rule-relevance check (Gemini, A/B/C/D/ERR)           ×0.058    drops 94.2 %  ◄── DOMINANT CUT
        │      C = decorative (10,398, 79.7 %): bug fix unrelated
        │             to any documented rule
        │      D = unscaffoldable (1,896, 14.5 %): platform-specific,
        │             GPU-bound, > 500-line refactor, no testable
        │             behavior
        ▼
   750  ██▊                                                            3.86  A + B wins (A=204, B=546)
        │
        │  A5 — Opus 4.7 builds the task + Docker test                ×~0.72    drops ~28 %
        │       (build → no fix → 0; gold → 1).
        │       Failed builds are quarantined.
        ▼
  ≈540  ██                                                             ≈2.8   valid built tasks
```

**Per-PR yield: 2.8 % per pass.** The dominant cut is **A4** (the rule-relevance check): 94 % of admitted PRs are class C — bug fixes that any agent could write without ever opening a rule file.

### 9.3 Same shape, different orderings

Both pipelines lose ≈ 99 % of their raw input to enforce one principle: *every surviving task's gold fix must be shaped by the rule files.* They differ only in *where* in the funnel they push the work onto the LLM:

| | Pipeline A | Pipeline B |
|---|---|---|
| How A4 (rule-relevance) is enforced | Gemini call on every candidate PR's metadata + diff | Path regex first (free; pure-rule-file PRs are tautologically "shaped by" the rules), then Gemini on the gold patch |
| Where the dominant cut lands | Stage 7.3, ≈ 94 % drop | Stage 8.1.1, ≈ 97 % drop |
| Cost shape | Pays a Gemini call on every candidate (≈ 13 K) | Pays a Gemini call only on the path-regex survivors (≈ 320) |

A benchmark retaining 30 % of merged PRs would be silent on instruction-following — exactly the failure mode the inclusion criterion (§2) exists to prevent. The narrow yield is the price of having every surviving task carry a clean signal.

## 10. Quality gate criteria (Pipeline B post-judge thresholds)

The post-judge prompt asks Gemini for four structured fields, then computes the verdict deterministically from them.

- **`load_bearing`** ∈ {true, false}: would an agent *reading* this gold patch produce different downstream behavior than an agent that *ignored* it? Falsified by generic prose, self-referential meta-content, pure formatting changes, lockfile-style updates, frontmatter-only PRs.
- **`research_relevant`** ∈ {true, false}: does this PR fit our benchmark's schema? Falsified when the file is technically a rule file but the change carries no behavioral assertion an agent could either follow or violate.
- **`slop_score`** ∈ [0, 10]: 0 = concrete commands / file paths / version pins / anti-pattern rules. 10 = AI-generated boilerplate / auto-bot output / generic prose any LLM could produce without context.
- **`verdict`**:
  - HIGH iff `slop_score ≤ 3` and both flags are true,
  - MEDIUM iff `4 ≤ slop_score ≤ 6` and both flags are true,
  - LOW iff `7 ≤ slop_score ≤ 8`,
  - DELETE iff `slop_score ≥ 9` or either flag is false.

The judge is instructed to default to reject when in doubt. The asymmetry: a false positive (slop task in the corpus) silently weakens the benchmark; a false negative (a real task moved to quarantine) just costs us one task out of hundreds.

## 11. Why two pipelines

Markdown-only PRs do not need an agent to design a test, choose files, or run Docker. The transformation from PR-diff to task is mechanical (extract distinctive lines, grep for them in the agent's output). When we previously routed these through Pipeline A's Opus + sandbox flow, the LLM occasionally invented additional files or paraphrased the diff, breaking the verbatim grep and producing flaky tasks. Pipeline B's deterministic script produces tighter behavioral tests at much lower marginal effort per task. The trade-off is one strict asymmetry — the test is verbatim, so a competent agent that paraphrases the gold answer fails. The post-judge rejects PRs where this asymmetry is severe.

For Pipeline A the same logic does not apply. Deciding which test to write, where to write it, and how to phrase the instruction so the agent's path to a fix is non-trivial all require a model strong enough to read the repository structure. We retain Opus there.

## 12. Failure modes observed in production

Identified during the 2026-04-27 batch. Each is documented for reproducibility and to clarify why the post-judge is necessary even with the upstream filters.

- **Auto-bot PRs** — *26 of 104 LOW + DELETE, by repository origin.* One repository (PrefectHQ) runs an automated commit-watcher that opens "Update AGENTS.md for commit X" PRs after each push to main. These pass the rule-file regex but contain no human-curated content. The pre-judge catches title-level cases; the post-judge catches the rest by detecting "Automated AGENTS.md update" in the PR body.
- **Broken-yaml manifests** — *33 of 104.* A bug in the build script, identified and fixed mid-run, emitted `eval_manifest.yaml` files with mixed-indent YAML block scalars when the gold patch contained outdented lines. The judge correctly rejected these via `yaml.safe_load` failure.
- **Generic AI-authored skills and boilerplate** — *residual ≈ 30–50.* PRs adding net-new SKILL.md files whose bodies are generic prose ("This skill helps with X") with no concrete commands, file paths, or anti-patterns. The task prompt offers nothing the agent could not invent independently, so the verbatim-grep test is unreliable.
- **Self-referential meta-content** — *3 of 104.* "Add a skill for managing skills" — passes the regex, fails rule-relevance.

## 13. Reproducibility

Per-row decision logs are checked into the repository for the 2026-04-27 batch:

- `scouted_scaleup_v2_prejudged.decisions.csv`, `scouted_round2_v2_prejudged.decisions.csv` — pre-judge decisions for every PR considered, with verdict and ≤ 12-word reason.
- `pipeline_logs/scaffold_v4_2026_04_26/md_quality_v2_combined.json` — post-judge structured output for every task (`load_bearing`, `research_relevant`, `slop_score`, `evidence`, `verdict`).

All Gemini calls use temperature 0.1, structured output via `responseMimeType: "application/json"` + `responseSchema`, and a thinking budget of 256 tokens. Discovery queries are listed verbatim in §6.

## 14. Limitations

- **Verbatim-grep tests** in Pipeline B reward agents that produce exactly the gold prose. A competent agent that produces semantically equivalent but textually different content fails. Mitigated by the post-judge, not eliminated.
- **Single-classifier post-judge** in Pipeline B. We do not currently run a second-classifier cross-check, in contrast to Pipeline A which historically used a Kimi → Gemini → Kimi cross-validation loop.
- **Recency window asymmetry**. Pipeline A uses 12 months, Pipeline B uses 24. Yield-rate comparisons across the two pipelines are not strictly apples-to-apples.
- **Fallback path during Gemini Flex outages**. The Flex tier returned 503 UNAVAILABLE for sustained periods on 2026-04-27; the pipeline's auto-fallback to Standard tier restored throughput.
- **The rule-file definition is closed**. Any new agent-instruction file format must be added to the regex by hand before the pipeline recognizes it.
- **No batch-provenance tracking** in the post-judge. We cannot directly attribute the 104 LOW + DELETE verdicts in the 2026-04-27 batch to the 214 newly-built tasks vs. the 608 pre-existing ones; the §12 attribution is by inferred origin (e.g., PrefectHQ-bot PRs were built in earlier passes).
