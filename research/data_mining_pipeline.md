# Data Construction Methods

This document specifies how we mine merged GitHub PRs and convert them into runnable benchmark tasks. The protocol produces two complementary corpora — code-fix tasks and markdown-authoring tasks — both released as pre-built Docker images on `ghcr.io/findalexli/agentsmd-rl/<task>:latest`.

**Corpus snapshot (2026-04-27).**

| Corpus | Active | What the test asserts | Scaffold | Quality gate |
|---|---:|---|---|---|
| `harbor_tasks/` | 582 | Reward = 1 iff the agent reproduces the gold code fix | Claude Opus 4.7 in an isolated sandbox | Docker oracle + LLM rubric judge |
| `harbor_tasks_md_authoring/` | 718 | Reward = 1 iff the agent's output contains the distinctive added lines from the gold patch | Deterministic transform (no LLM) | Two-stage Gemini 3.1 Pro judge |
| **Total** | **1,300** | | | |

---

## 1. What this benchmark tests

Whether an AI coding agent reads and follows project-specific *agent-instruction files* — `CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `.cursor/rules/*` and similar — when it modifies code or writes new instructions.

The challenge is constructing tasks for which the *correct* answer is determined in part by what those rule files say. A task whose gold solution would be the same regardless of the rule files is silent on instruction-following: an agent that ignores the rules can still pass it.

## 2. Core assumption

> **A merged PR is a useful benchmark task only when its gold diff is *causally shaped by the agent-instruction surface* — i.e., the diff would have looked materially different if the repo's tier-1 instruction files had been absent.**

Every filter in this pipeline is in service of that assumption. PRs that fail it produce tasks where reward is uninformative about whether the agent attended to the rules.

## 3. Definitions

**Tier-1 instruction file.** A closed set of paths matched by one regex:

> `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `CONVENTIONS.md`, `SKILL.md`, `.cursorrules`, `.windsurfrules`, `.clinerules`, `.continuerules`, `*.mdc`, `.claude/{rules,skills,agents}/*.md`, `.cursor/rules/*`, `.github/copilot-instructions.md`, `.github/skills/*/SKILL.md`, `.github/prompts/*.prompt.md`, `.{agents,opencode,codex}/skills/*/SKILL.md`.

A repository is **agent-instruction equipped** if it contains at least one tier-1 file.

**PR class** (the outcome of the causality judgment):

| Class | The gold diff... | Outcome |
|---|---|---|
| **A** | edits a tier-1 file | Keep — markdown-authoring task |
| **B** | is code-only, but the fix encodes a rule documented in a tier-1 file | Keep — code-fix task |
| **C** | is determined entirely by the bug, independent of any rule | Drop — decorative |
| **D** | is technically unscaffoldable on Linux Docker (platform-specific runtime, GPU, multi-thousand-line refactor, no testable behavior) | Drop — unscaffoldable |

**Docker oracle.** An automated test on a freshly-built task image asserting (a) base commit produces reward = 0, (b) gold patch produces reward = 1. Tasks failing either assertion are quarantined.

## 4. Assumptions and the filters that enforce them

Every drop in the pipeline maps to one of five assumptions. We list each assumption with the filter that enforces it and the empirical drop rate observed in the 2026-04-27 batch.

| # | Assumption | Filter | Drop rate (this batch) |
|---|---|---|---|
| **A1** | The repository contains agent-instruction files an agent could read | Discovery via `gh search repos` (topics + `SKILL.md`/`.claude/skills`/`.cursor/rules` path queries) and ≥ 5-star threshold | upstream of the funnel (repo selection) |
| **A2** | The PR is a clean, scaffoldable unit of work | Scout-time PR filters: `changedFiles ∈ [1, 8]`, `additions + deletions ∈ [5, 500]`, no `wontfix`/`dependencies`/`automated-update` labels, recency window | 67.6% of raw fetched (29,733 → 9,629) |
| **A3** | The PR's diff content is in scope for the chosen pipeline | **Pipeline A**: tier-1 *repo* allowlist + slug-dedup against existing corpus. **Pipeline B**: tier-1 *path* regex (every changed file matches) | A: 41.5% (14,549 → 13,046 after dedup); B: 96.7% (9,629 → 321) |
| **A4** | The gold fix is causally shaped by the agent-instruction surface (the core assumption from §2) | **Pipeline A**: Gemini causality judge → A/B/C/D. **Pipeline B**: structured Gemini judges on title (pre-scaffold) and gold patch (post-scaffold) → load_bearing × research_relevant × slop_score → HIGH/MEDIUM/LOW/DELETE | A: 94.2% drop (12,294 of 13,046 are C/D/ERR); B: 5.9% pre-judge + 12.7% post-judge |
| **A5** | The task is mechanically scaffoldable into a runnable Docker oracle | **Pipeline A**: Opus scaffold + Docker oracle (build, nop=0, gold=1). **Pipeline B**: deterministic transform with idempotency check; broken-yaml manifests rejected by judge | A: ≈25-30% scaffold-fail; B: ≈1% transform-fail |

The pipelines split on A3: Pipeline A admits any code-bearing PR from a tier-1-equipped repo, then leans heavily on A4's causality judge. Pipeline B starts strict on A3 (every path must be a tier-1 file) so the LLM judges in A4 are smaller and cheaper. PRs filtered out at Pipeline B's A3 are not lost — they are routed to Pipeline A's queue.

## 5. The two pipelines at a glance

| | Pipeline A — code-fix | Pipeline B — markdown-authoring |
|---|---|---|
| Diff content kept | Code (with optional tier-1 edits) | Tier-1 only |
| Pre-classifier filter | Tier-1 *repo* allowlist | Tier-1 *path* regex |
| Classifier | Gemini causality (A/B/C/D) | Gemini structured Verdict (pre-judge + post-judge) |
| Scaffold | Opus 4.7 inside an E2B sandbox | Deterministic: shallow-clone + apply gold + grep for distinctive `+` lines |
| Validation | Docker oracle | Built into the verbatim-grep test |
| Latest scout window | 12 months | 24 months |
| Latest scout repos | 147 | 1,037 |
| Cumulative active tasks | 582 | 718 |

## 6. Discovery and scout (shared by both pipelines)

**Discovery.** Query `gh search repos` across thirteen agent-instruction-related topics (`claude-code`, `claude-skills`, `claude-agents`, `agent-skills`, `agents-md`, `claude-md`, `cursor-rules`, `awesome-skills`, `awesome-claude-code`, `claude-plugins`, `claude-code-skill`, `agent-instructions`, `llm-rules`) and three repository-content paths (`SKILL.md in:path`, `.claude/skills in:path`, `.cursor/rules in:path`). Sort by stars; aggregate top 200–300 per query; retain ≥ 5-star repos; deduplicate against earlier passes.

**Scout.** For each retained repository, issue `gh pr list --state merged --json number,title,changedFiles,additions,deletions,mergedAt,labels,mergeCommit,files`, capped at 200 PRs per call (above 200, GitHub's GraphQL endpoint returns 504 on large repositories). Including `files` at scout time returns each PR's full path list and avoids ~50× of subsequent REST `/files` calls in Pipeline B. Apply the scout-time PR filters (assumption A2).

| Pipeline | Repos scouted | Raw merged PRs fetched | Candidates after A2 |
|---|---:|---:|---:|
| A — Code-fix (2026-04-26 pass) | 107 | 19,417 | 14,549 |
| B — Markdown-authoring (2026-04-27 batch) | 1,037 | 29,733 | 9,629 |

## 7. Pipeline A — Code-fix tasks

Numbers are for the 2026-04-26 scout pass; the cumulative `harbor_tasks/` corpus is the result of multiple such passes accumulated over weeks.

| Stage | Filter | Enforces | In | Drop | Out |
|---|---|---|---:|---:|---:|
| 7.1 Slug-dedup | Drop PRs already in the baseline corpus (slug + `(repo, pr)` key) | A3 | 19,417 | 4,868 | 14,549 |
| 7.2 Tier-1 repo allowlist | Drop PRs from repos without a confirmed tier-1 file | A3 | 14,549 | 1,503 | 13,046 |
| 7.3 Causality judge | Gemini 3.1 Pro classifier → A / B / C / D / ERR | A4 | 13,046 | 12,294 | 750 (A=204, B=546) |
| 7.4 Opus scaffold + Docker oracle | One-shot Opus 4.7 call in an E2B sandbox: clone, apply gold, write tests, validate via oracle | A5 | 750 | ≈25-30% | ≈530-560 valid |
| 7.5 Quality gate | LLM rubric audit; tier-A/B failures quarantined | A5 | ≈540 | small | merged into corpus |

**Cumulative corpus**: 582 active in `harbor_tasks/`, 92.8% Docker-oracle pass rate (540 pass / 41 fail / 1 missing). End-to-end yield this pass: ≈540 / 19,417 ≈ **2.8%**.

The dominant cut is the causality judge (7.3): without it, ≈94% of admitted PRs are class C. The benchmark would then be silent on whether the agent attended to the rule files.

## 8. Pipeline B — Markdown-authoring tasks

Pipeline B targets PRs that *only* edit tier-1 files, so the transformation from PR to task is mechanical: extract the most distinctive added lines, assert their presence in the agent's output. We replace the per-task Opus call with a deterministic procedure flanked by two Gemini quality gates — a cheap title-level screen before scaffolding and a full-context judge after.

### 8.1 New-candidate pipeline (chains 9,629 → 214)

| Stage | Filter | Enforces | In | Drop | Out |
|---|---|---|---:|---:|---:|
| 8.1.1 Tier-1 path regex | Every changed path must match the tier-1 regex; PRs with any non-tier-1 path are routed to a side queue (`_codebearing.jsonl`, 34,358 cumulative rows) for Pipeline A's processing later | A3 | 9,629 | 9,308 | **321** |
| 8.1.2 Pre-judge | Gemini 3.1 Pro Standard, input = `{repo, title, file_paths}` only. Drops bot-generated titles, dummy-test PRs, version-bump-only titles, generic boilerplate. Conservative — defaults to KEEP | A4 | 321 | 19 | 302 |
| 8.1.3 Deterministic scaffold | Shallow-clone at base SHA, generate Dockerfile + `solve.sh` (applies gold patch verbatim) + `tests/test_outputs.py` (N=3 distinctive `+` lines, ≥ 12 chars, non-trivial alphanumeric, deduplicated) + `eval_manifest.yaml` v2.0. No LLM call | A5 | 302 | 88 idempotent slug-collisions | **214 newly scaffolded** |

### 8.2 Corpus re-validation (independent count, 822 → 718)

The post-judge runs across the full corpus state at judge time — the 214 just scaffolded plus 608 pre-existing tasks from earlier scouts — and re-validates each.

| Stage | Filter | Enforces | In | Drop | Out |
|---|---|---|---:|---:|---:|
| 8.2.1 Post-judge | Gemini 3.1 Pro Standard, full context: `instruction.md` + complete gold patch. Outputs structured `Verdict { load_bearing, research_relevant, slop_score, evidence, verdict ∈ {HIGH, MEDIUM, LOW, DELETE} }`. Verdict thresholds in §10 | A4 | 822 | 104 | 706 HIGH + 12 MEDIUM |
| 8.2.2 Quarantine | Move LOW + DELETE to `harbor_tasks_md_authoring_quarantine_quality/` (keeps `md_quality.json` audit trail per task) | — | 104 | — | **718 active** |

Cumulative active yield: 718 / 9,629 ≈ **7.5%**. Per-batch new-task yield: 214 / 9,629 ≈ **2.2%**.

## 9. The funnel — where every PR goes

Both pipelines end with the same yield (~2-3% per pass) but the cuts arrive in different orders. The waterfalls below show where each pipeline loses volume. **Bar widths are proportional to share-of-raw**; the dominant drop in each pipeline is marked.

### 9.1 Pipeline B — Markdown-authoring (2026-04-27 batch)

```
                                                                              %  of raw
29,733  ████████████████████████████████████████████████████████████████████  100.00  raw merged PRs from 1,037 repos
        │
        │  A2 — scout-time PR hygiene (size, labels, recency)         ×0.324   drops 67.6 %
        ▼
 9,629  ██████████████████████                                         32.39  candidates after scout filters
        │
        │  A3 — tier-1-only path regex                                 ×0.033   drops 96.7 %  ◄── DOMINANT CUT
        │      (the other 96.7 % mix code with markdown and route to
        │       Pipeline A's codebearing queue, not lost)
        ▼
   321  ▊                                                               1.08  pure-tier-1 PRs
        │
        │  A4 — pre-judge title screen (Gemini, no patch context)      ×0.941   drops 5.9 %
        ▼
   302  ▊                                                               1.02  scaffolder inputs
        │
        │  scaffold transform (88 idempotent slug-collisions —
        │  these PRs were already scaffolded in earlier scouts)
        ▼
   214  ▌                                                               0.72  newly-scaffolded task dirs
        │
        │  A4 — post-judge on merged 822-task corpus (Gemini, full     ×~0.85   drops 12.7 %
        │       gold-patch context). The new-task share of these
        │       drops is unattributed — see §14.
        ▼
   ≈180  ▌                                                              ≈0.6   net new HIGH/MEDIUM tasks added by this batch
```

**Per-PR new-task yield: 0.72 %.** The dominant cut is **A3** (the path regex): 96.7 % of candidates touch at least one non-tier-1 file. This is structural — Pipeline B's deterministic transform only works on pure-rule-file diffs, so anything mixed routes to Pipeline A.

### 9.2 Pipeline A — Code-fix (2026-04-26 scout pass)

```
                                                                              %  of raw
19,417  ████████████████████████████████████████████████████████████████████  100.00  raw merged PRs from 107 repos
        │
        │  A3 — slug-dedup against the baseline corpus                 ×0.749   drops 25.1 %
        ▼
14,549  ███████████████████████████████████████████████████             74.93  unique new PRs
        │
        │  A3 — tier-1 repo allowlist                                  ×0.897   drops 7.7 %
        ▼
13,046  ██████████████████████████████████████████████                 67.19  PRs into the judge
        │
        │  A4 — causality judge (Gemini, A / B / C / D / ERR)          ×0.058   drops 94.2 %  ◄── DOMINANT CUT
        │      C = decorative (10,398, 79.7 %): bug fix unrelated
        │             to any documented rule
        │      D = unscaffoldable (1,896, 14.5 %): platform-specific,
        │             GPU-bound, >500-line refactor, no testable behavior
        ▼
   750  ██▊                                                              3.86  A + B wins (A=204, B=546)
        │
        │  A5 — Opus 4.7 scaffold + Docker oracle (build, nop=0,        ×~0.72   drops ~28 %
        │       gold=1). Failed scaffolds are quarantined.
        ▼
  ≈540  ██                                                               ≈2.8  valid scaffolded tasks
```

**Per-PR yield: 2.8 % per pass.** The dominant cut is **A4** (the causality judge): 94 % of admitted PRs are class C (decorative) — their bug fix is determined by the bug, not by any rule.

### 9.3 The same shape, different orderings

Both pipelines lose ~99 % of their raw input to enforce one principle: *every surviving task's gold fix must be causally shaped by the rule files.* The pipelines differ in *where* in the funnel they operationalize this:

| | Pipeline A | Pipeline B |
|---|---|---|
| Core enforcement of A4 (causality) | LLM judge over PR metadata + diff | Path regex (proxy: pure-rule-file PRs are tautologically "shaped by" the rules) + LLM judge over gold patch |
| Where the dominant cut lands | Stage 7.3, ~94 % drop | Stage 8.1.1, ~97 % drop |
| Cost shape | Pays per-PR Gemini call on every candidate (13K) | Pays Gemini calls only on the ~321 path-regex survivors |

A benchmark retaining 30 % of merged PRs would be silent on instruction-following — exactly the failure mode the inclusion criterion (§2) exists to prevent. The narrow yield is the cost of having every surviving task carry a clean signal.

## 10. Quality gate criteria (Pipeline B post-judge thresholds)

The post-judge prompt asks Gemini for four structured fields and a verdict computed from them:

- **`load_bearing`** ∈ {true, false}: would an agent reading vs. ignoring this gold patch produce different downstream behavior? Falsified by generic prose, self-referential meta-content, pure formatting changes, lockfile-style updates, frontmatter-only PRs.
- **`research_relevant`** ∈ {true, false}: does the PR fit the agent-md research schema? Falsified when the file is technically tier-1 but the change carries no behavioral assertion an agent could either follow or violate.
- **`slop_score`** ∈ [0, 10]: 0 = concrete commands / file paths / version pins / anti-pattern rules; 10 = AI-generated boilerplate / auto-bot output / content any LLM could produce without context.
- **`verdict`** computed deterministically from the above:
  - HIGH iff `slop_score ≤ 3` and both flags true,
  - MEDIUM iff `4 ≤ slop_score ≤ 6` and both flags true,
  - LOW iff `7 ≤ slop_score ≤ 8`,
  - DELETE iff `slop_score ≥ 9` or either flag false.

The judge defaults to reject when in doubt. The asymmetry: a false positive (decorative task in the corpus) silently weakens the benchmark; a false negative (real task quarantined) just means we lose one task out of hundreds.

## 11. Why two pipelines

Markdown-only PRs do not require an agent to design tests, choose files, or run Docker; the transformation from PR-diff to scaffolded task is mechanical (extract distinctive added lines, grep for them in the agent's output). Routing them through the Opus + sandbox pipeline produced lower-quality tasks — the LLM occasionally invented additional files or paraphrased the diff, breaking the verbatim grep. Pipeline B produces tighter behavioral tests at much lower marginal effort per task, in exchange for one strict asymmetry: the test is verbatim, so a competent agent that paraphrases the gold answer fails. The post-judge rejects PRs where this asymmetry is severe.

For Pipeline A the same logic does not apply: deciding which test to write, where to write it, and how to phrase the instruction so that the agent's path to a fix is non-trivial all require a model strong enough to read the repository structure. We retain Opus there.

## 12. Failure modes observed in production

Identified during the 2026-04-27 batch. Each is documented for reproducibility and to clarify why the post-judge is necessary even with the upstream filters.

- **Auto-bot PRs** (26 of 104 LOW + DELETE, by repository origin): one repository (PrefectHQ) runs an automated commit-watcher that opens "Update AGENTS.md for commit X" PRs after each push to main. These pass the tier-1 path regex but contain no human-curated content. Pre-judge catches title-level cases; post-judge catches the rest by detecting "Automated AGENTS.md update" in the PR body.
- **Broken-yaml manifests** (33 of 104): a scaffolder bug, identified and fixed mid-run, emitted `eval_manifest.yaml` files with mixed-indent YAML block scalars when the gold patch contained outdented lines. The judge correctly rejected these via `yaml.safe_load` failure.
- **Generic AI-authored skills and boilerplate** (residual ≈30-50): PRs adding net-new SKILL.md files whose bodies are generic prose ("This skill helps with X") with no concrete commands, file paths, or anti-patterns. The task prompt offers nothing the agent could not invent independently, so the verbatim-grep test is unreliable.
- **Self-referential meta-content** (3 of 104): "Add a skill for managing skills" — passes the regex, fails causality.

## 13. Reproducibility

Per-row decision logs are checked into the repository for the 2026-04-27 batch:

- `scouted_scaleup_v2_prejudged.decisions.csv`, `scouted_round2_v2_prejudged.decisions.csv` — pre-judge decisions for every PR considered, with verdict and ≤ 12-word reason.
- `pipeline_logs/scaffold_v4_2026_04_26/md_quality_v2_combined.json` — post-judge structured output for every scaffolded task (`load_bearing`, `research_relevant`, `slop_score`, `evidence`, `verdict`).

Gemini calls use temperature 0.1, structured output via `responseMimeType: "application/json"` + `responseSchema`, and a thinking budget of 256 tokens. Discovery queries are listed verbatim in §6.

## 14. Limitations

- **Verbatim-grep tests** in Pipeline B reward agents that produce exactly the gold prose. A competent agent that produces semantically equivalent but textually different content fails. Mitigated by the post-judge, not eliminated.
- **Single-classifier post-judge** in Pipeline B. We do not currently run a second-classifier cross-check, in contrast to Pipeline A which historically used a Kimi → Gemini → Kimi cross-validation loop.
- **Recency window asymmetry**. Pipeline A uses 12 months, Pipeline B uses 24. Yield-rate comparisons across the two pipelines are not strictly apples-to-apples.
- **Auto-fallback path during Gemini Flex outages**. The Flex tier returned 503 UNAVAILABLE for sustained periods on 2026-04-27; the pipeline's auto-fallback to Standard tier restored throughput.
- **Tier-1 file definition is closed**. Any new agent-instruction file format must be added to the regex by hand before it is recognized.
- **No batch-provenance tracking** in the post-judge. We cannot directly attribute the 104 LOW + DELETE verdicts in the 2026-04-27 batch to the 214 newly-scaffolded tasks vs. the 608 pre-existing ones; §12 attribution is by inferred origin (e.g. PrefectHQ-bot PRs were scaffolded in earlier passes).
