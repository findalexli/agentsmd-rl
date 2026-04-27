# Data Construction Methods

This document specifies how we mine merged GitHub PRs and convert them into runnable benchmark tasks. The protocol produces two complementary corpora: code-fix tasks and markdown-authoring tasks. Both are released with pre-built Docker images.

**Current corpus** (snapshot 2026-04-27):

| Corpus | Active tasks | Diff content tested | Scaffold method | Quality gate |
|---|---|---|---|---|
| `harbor_tasks/` | 582 | Code change that depends on a documented rule | Claude Opus 4.7 in an isolated sandbox | Docker oracle (build, run, expect reward 0/1) + LLM rubric judge |
| `harbor_tasks_md_authoring/` | 718 (706 HIGH + 12 MEDIUM) | Edits to agent-instruction files only | Deterministic transform — no LLM | Two-stage Gemini 3.1 Pro judge |

Both corpora ship as images on `ghcr.io/findalexli/agentsmd-rl/<task>:latest`. Combined: **1,300 active tasks**.

---

## 1. Definitions

**Tier-1 instruction file**: a file in a repository whose content is *intended* to be read by an AI coding agent before it modifies code. We define this as a closed set of paths matched by a single regex:

> `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `CONVENTIONS.md`, `SKILL.md`, `.cursorrules`, `.windsurfrules`, `.clinerules`, `.continuerules`, `*.mdc`, `.claude/{rules,skills,agents}/*.md`, `.cursor/rules/*`, `.github/copilot-instructions.md`, `.github/skills/*/SKILL.md`, `.github/prompts/*.prompt.md`, `.{agents,opencode,codex}/skills/*/SKILL.md`.

A repository is **agent-instruction equipped** if it contains at least one tier-1 file.

**Inclusion criterion**: a merged PR enters the benchmark only when its gold fix is *causally shaped by the agent-instruction surface* — that is, the diff would have looked materially different if the repo's tier-1 files had been absent. PRs are categorized into four classes:

| Class | The gold diff... | Outcome |
|---|---|---|
| **A** | edits a tier-1 file | Keep — markdown-authoring task |
| **B** | is code-only, but the fix encodes a rule documented in a tier-1 file | Keep — code-fix task |
| **C** | is determined entirely by the bug, independent of any rule | Drop — decorative |
| **D** | is technically unscaffoldable on Linux Docker (platform-specific runtime, GPU, multi-thousand-line refactor, no testable behavior) | Drop — unscaffoldable |

**Docker oracle**: an automated test on a freshly-built task image that asserts (a) running with the *base* commit produces reward = 0, and (b) running after the *gold* patch produces reward = 1. Tasks failing the oracle are quarantined.

**Per-PR yield**: number of final benchmark tasks produced per PR fetched from GitHub.

---

## 2. Repository discovery

A single discovery step feeds both pipelines. We query `gh search repos` across thirteen agent-instruction-related topics and three repository-content paths, sort by stars, and aggregate the top 200–300 results per query:

> Topics queried: `claude-code`, `claude-skills`, `claude-agents`, `agent-skills`, `agents-md`, `claude-md`, `cursor-rules`, `awesome-skills`, `awesome-claude-code`, `claude-plugins`, `claude-code-skill`, `agent-instructions`, `llm-rules`.
> Path queries: `SKILL.md in:path`, `.claude/skills in:path`, `.cursor/rules in:path`.

We retain repositories with **≥ 5 stars** (excludes empty/abandoned projects) and deduplicate against repositories scouted in earlier passes.

| Pipeline run | Recency window | Unique repos retained |
|---|---|---|
| Code-fix corpus, latest scout pass (2026-04-26) | 12 months | 147 |
| Markdown-authoring corpus, batch 2026-04-27 | 24 months | 1,037 |

The markdown run uses a longer window and a broader topic set because per-repo yield of *pure*-tier-1-path PRs is roughly half that of any-causality PRs (≈3% vs ≈6%); we compensate with breadth.

---

## 3. PR enumeration

For each retained repository we issue `gh pr list --state merged --json files,…`, capped at **200 PRs per call** (above 200, GitHub's GraphQL endpoint returns 504 on large repositories). Including the `files` field at scout time returns each PR's full path list, which eliminates ≈50× of subsequent REST `/files` calls in the markdown pipeline.

Per-PR scout-time exclusions:

- `changedFiles` not in `[1, 8]` (multi-file refactors are not clean benchmarks),
- `additions + deletions` not in `[5, 500]` (too small to be testable, too large to be tractable),
- carries any of the labels `wontfix`, `dependencies`, `automated-update`, `no-changelog`,
- merged before the recency cutoff,
- `docs_only` filter: drop if every changed file is documentation, *unless* every changed file is a tier-1 instruction file (the exemption preserves PRs that are pure rule edits — these are the input to the markdown pipeline).

| Pipeline | Repos scouted | Raw merged PRs fetched | Candidates after scout filters |
|---|---|---|---|
| Code-fix (2026-04-26 pass) | 107 | 19,417 | 14,549 |
| Markdown-authoring (2026-04-27 batch) | 1,037 | 29,733 | 9,629 |

The 14,549 → 13,046 transition in the code pipeline is a slug-deduplication against the cumulative baseline corpus (existing `(repo, pr)` pairs are skipped).

---

## 4. Pipeline A — Code-fix tasks

Each surviving PR receives a Gemini 3.1 Pro causality classification, then (for class A or B) a single Claude Opus 4.7 call inside an isolated sandbox produces the runnable task. Numbers below are for the **2026-04-26 scout pass**; the cumulative `harbor_tasks/` corpus is the result of multiple such passes accumulated over weeks.

| Stage | Mechanism | Input | Drop | Output |
|---|---|---|---|---|
| 4.1 Slug deduplication | Drop PRs already represented in the baseline (4,809 stubs); key on slug + `(repo, pr)` | 19,417 | 4,868 | 14,549 |
| 4.2 Tier-1 repo allowlist | Drop PRs from repositories with no confirmed tier-1 file | 14,549 | 1,503 | 13,046 |
| 4.3 Causality judge | Gemini 3.1 Pro classifier emitting one of {A, B, C, D, ERR} | 13,046 | 12,294 (C+D+ERR) | A=204, B=546, total = **750** |
| 4.4 Opus scaffold + Docker oracle | One-shot Claude Opus 4.7 call inside an E2B sandbox: clone repo, apply gold patch, generate `instruction.md` / `solve.sh` / `tests/test.sh` / `eval_manifest.yaml`, validate via Docker oracle | 750 | ≈25-30% scaffold-fail | ≈530-560 valid |
| 4.5 Quality gate | LLM rubric audit (post-scaffold); tier-A/B failures moved to quarantine | ≈540 | small | merged into the cumulative corpus |

**Cumulative corpus**: 582 active tasks in `harbor_tasks/` (as of 2026-04-27), 92.8% Docker-oracle pass rate (540 pass / 41 fail / 1 missing oracle status).

**End-to-end yield (single pass)**: ≈540 / 19,417 ≈ 2.8%.

The dominant filter is the **causality judge** (stage 4.3): without it, ≈94% of admitted PRs are class C (decorative) — a benchmark constructed from those would be silent on whether the agent attended to the rule files, which is the failure mode the inclusion criterion is designed to prevent.

---

## 5. Pipeline B — Markdown-authoring tasks

Pipeline B targets the subset of PRs that *only* edit tier-1 instruction files. The transformation from such a PR to a runnable benchmark task is mechanical (extract the most distinctive added lines, assert their presence in the agent's output), so we replace the per-task Opus call of Pipeline A with a deterministic procedure flanked by two Gemini quality gates: one cheap title-level screen before scaffolding, and one full-context judge after. All numbers below are for the **2026-04-27 batch**.

The pipeline is five stages, summarized in Table 5.1 and detailed in §5.1–§5.5 below.

**Table 5.1.** Pipeline B funnel. Stages 5.1–5.3 chain cleanly on the new candidate pool. Stage 5.4 is a *re-validation pass* over the full corpus state at the time of judging, which includes both the 214 new tasks just scaffolded and 608 pre-existing tasks from earlier scouts; we keep its accounting separate so the per-stage math stays transparent.

*New-candidate pipeline (chains 9,629 → 214):*

| Stage | Filter | In | Drop | Out |
|---|---|---|---|---|
| 5.1 Path regex | Tier-1-only (every changed path) | 9,629 | 9,308 | **321** |
| 5.2 Pre-judge | Gemini, title-only | 321 | 19 | 302 |
| 5.3 Scaffold | Deterministic transform | 302 | 88 (slug-collisions with existing corpus) | **214 newly scaffolded** |

*Corpus re-validation (independent count, 822 → 718):*

| Stage | Filter | In | Drop | Out |
|---|---|---|---|---|
| 5.4 Post-judge | Gemini, full gold-patch context | **822** = 608 pre-existing + 214 new from §5.3 | 104 (LOW + DELETE) | 718 (706 HIGH + 12 MEDIUM) |
| 5.5 Quarantine | Move LOW + DELETE to `harbor_tasks_md_authoring_quarantine_quality/` | 104 | — | **718 active in corpus** |

### 5.1 Path regex pre-filter

A PR survives iff *every* path in its diff matches the tier-1 regex (defined in §1). PRs touching any non-tier-1 path — even a single test fixture or generated file — are routed instead to a side queue (`scaffold_queue_*_codebearing.jsonl`, 34,358 rows cumulative across all 2026-04 scouts) and held for future Pipeline A processing. The regex is the work-horse filter: it discards 9,308 of 9,629 candidates (96.7%) without a single API call.

### 5.2 Pre-judge

Gemini 3.1 Pro Standard tier, structured-output classifier with input restricted to `{repo, title, file_paths}` — no PR body, no diff. The prompt directs the model to return KEEP unless the title is unambiguously slop. Surface-level rejection patterns the prompt enumerates explicitly:

- bot-generated titles (e.g. *"Automated AGENTS.md update for commit ABC"*),
- test or CI scaffolding (*"test: broken merge-batch e2e PR"*, *"DO NOT MERGE"*),
- pure metadata or version-bump titles (*"bump skill version to 1.0.1"*, *"add tags"*),
- generic boilerplate (*"Add comprehensive guide for X"* with no specific feature).

Conservative by design — the prompt instructs the model to default to KEEP when in doubt, deferring strict rejection to the post-judge (§5.4) which has the gold patch. Drops 19 of 321 (5.9%).

### 5.3 Deterministic scaffold

For each PR that passes pre-judge:

1. Shallow-clone the repository at the base commit SHA (`git init && git fetch --depth=1 origin <SHA>`).
2. Emit a `Dockerfile` based on the project's primary language detected from file paths (Python, Node, Rust, Go, generic).
3. Emit `solution/solve.sh` that applies the PR's gold diff verbatim via `git apply <<'PATCH'`.
4. Emit `tests/test_outputs.py` containing **N = 3** pytest assertions, one per distinctive added line. A line is *distinctive* if it is among the longest `+` lines in the diff after these filters: length ≥ 12 characters, contains non-trivial alphanumeric content, deduplicated against earlier picks. Each assertion checks `assert <line> in <target_file_text>`.
5. Emit `eval_manifest.yaml` (schema v2.0) with `task.kind = markdown_authoring` and one entry per changed file in `config_edits`.

The transform involves zero LLM calls. Per-attempt success rate is approximately 99%; the residual ~1% are edge cases (e.g. patches consisting entirely of removals, no `+` lines to extract). Of the 302 PRs entering this stage, 214 produce new task directories; the remaining 88 collide with task slugs already present in `harbor_tasks_md_authoring/` from earlier scout passes and are skipped under an idempotency check.

### 5.4 Post-judge

Gemini 3.1 Pro Standard tier, structured-output classifier with full context: the scaffolded task's `instruction.md` (PR description) and the complete gold patch as it appears in `eval_manifest.yaml`'s `config_edits[].gold_added`. The judge produces a structured `Verdict` object:

```
load_bearing       : bool       # would the gold patch change downstream agent behavior?
research_relevant  : bool       # is the change in scope for the agent-md research schema?
slop_score         : int 0..10  # 0 = concrete rule, 10 = AI/boilerplate
evidence           : string     # one quoted phrase from the diff supporting the score
verdict            : enum       # HIGH | MEDIUM | LOW | DELETE
```

The verdict is determined deterministically from the structured fields per the threshold table in §6. Stage 5.4 is run on the full corpus state at judge time (822 tasks: 608 pre-existing + 214 newly scaffolded), with caching (`md_quality.json` written per task) so re-runs skip already-judged tasks unless explicitly re-judged.

Outcomes for the 822 tasks judged in this pass:

| Verdict | Count | Share | Outcome |
|---|---:|---:|---|
| HIGH | 706 | 85.9% | Keep |
| MEDIUM | 12 | 1.5% | Keep |
| LOW | 2 | 0.2% | Quarantine |
| DELETE | 102 | 12.4% | Quarantine |

### 5.5 Quarantine

LOW and DELETE verdicts are moved (preserving full task contents) to `harbor_tasks_md_authoring_quarantine_quality/`. The post-judge result remains attached as `md_quality.json` inside each quarantined task, providing an audit trail. **718 tasks remain active** in `harbor_tasks_md_authoring/` (706 HIGH + 12 MEDIUM).

### 5.6 Yield analysis

Two yield definitions matter — they answer different questions and should not be conflated.

- **Per-batch new yield**: 214 newly scaffolded / 9,629 candidates ≈ **2.2%**. This is the relevant figure when forecasting how many tasks a future scout pass over a similar candidate distribution will add. It does *not* account for fresh tasks that may later be quarantined by the post-judge.
- **Cumulative active yield over the batch's candidate population**: 718 active tasks / 9,629 candidates ≈ **7.5%**. This counts all tasks currently active in `harbor_tasks_md_authoring/` against the 2026-04-27 batch's candidates. Most of the 718 were scaffolded in earlier scout passes; this batch's contribution is the 214 newly scaffolded minus whatever subset of them ended up LOW/DELETE in §5.4 (the exact split is not tracked directly; see below).

Filter contribution by stage:

- The path regex (§5.1) is dominant at 96.7% drop on the candidate pool (9,629 → 321).
- The pre-judge (§5.2) drops 19 of 321 (5.9%) using only title-level signal.
- The post-judge (§5.4) drops 104 of 822 (12.7%) on the *merged corpus*, using the full gold patch. Most of the 104 LOW + DELETE verdicts are concentrated in patterns that originate predominantly in earlier scaffold runs — auto-bot PRs from a single repository (≈26) and broken-yaml manifests from a since-fixed scaffolder bug (33) — rather than in the 214 newly scaffolded by this batch.

The pre-judge contributes a small absolute share because it has no patch content to reason over; the post-judge is the strict filter that ultimately determines what stays in the corpus.

### 5.7 Why ≈30K PRs become ≈200 new tasks

Three filters compose multiplicatively. Each removes a population we cannot validly include in this benchmark.

```
29,733  raw merged PRs from 1,037 agent-instruction-equipped repos
   ↓  ×0.324   scout-time PR filters: changedFiles ∈ [1,8],
              additions+deletions ∈ [5,500], skip {wontfix, dependencies,
              automated-update}, recency cutoff
 9,629  candidates
   ↓  ×0.033   tier-1-only path regex: every changed file must be an
              agent-instruction file. The other 96.7% mix code with
              markdown and are routed to the codebearing queue
              (Pipeline A's input, not Pipeline B's).
   321  pure-tier-1 PRs
   ↓  ×0.941   pre-judge title screen: drops bot-PRs, dummy tests,
              version-bump-only titles
   302  scaffolder inputs
   ↓  +88 idempotent skips (already in corpus from earlier scouts)
   214  newly scaffolded tasks
   ↓  ×~0.85   post-judge over the merged 822-task corpus drops 12.7%
              as LOW/DELETE; the new-task share is bounded above by this
   ≈180  net new HIGH/MEDIUM tasks added by this batch
```

Per-PR new-task yield ≈ 214 / 29,733 = **0.72%**. The two filters that dominate are mechanical (×0.324, scout-time hygiene) and structural (×0.033, tier-1-only paths).

**Why so many PRs drop at the path regex.** Even in repositories built around `CLAUDE.md` / `AGENTS.md` / `SKILL.md`, the vast majority of merged PRs are ordinary code work — bug fixes, feature additions, refactors — that may incidentally touch a doc file but mostly modify source code. Only about 1 in 30 PRs we scouted are *purely* rule-file edits. Pipeline B's deterministic scaffolder (verbatim-grep test on extracted `+` lines) only works on this narrow population. PRs that mix code with markdown are not lost; they are routed to a side queue for Pipeline A.

**Why the funnel is intentionally steep.** A benchmark that retained 30% of merged PRs would be silent on whether the agent attended to the rule files — exactly the failure mode the inclusion criterion (§1) is designed to prevent. The same logic applies to Pipeline A, where the *causality judge* (§4.3) drops 94% of admitted PRs as class C (decorative): the bug-fix is determined by the bug, not by any documented rule. Both pipelines pay the same kind of cost — high drop rate — for the same kind of property: every surviving task carries a clean instruction-following signal.

---

## 6. Quality gate criteria (markdown-authoring post-judge)

The post-judge prompt instantiates the inclusion criterion as four operational definitions:

- **`load_bearing`** (boolean): would an agent reading vs. ignoring this gold patch produce different downstream behavior? Falsified by generic prose, self-referential meta-content, pure formatting changes, lockfile-style updates, frontmatter-only PRs.
- **`research_relevant`** (boolean): does the PR fit the agent-md research schema? Falsified when the file is technically tier-1 but the change carries no behavioral assertion an agent could either follow or violate.
- **`slop_score`** ∈ [0, 10]: 0 = concrete commands / file paths / version pins / anti-pattern rules; 10 = AI-generated boilerplate / auto-bot output / content any LLM could produce without context.
- **`verdict`** ∈ {HIGH, MEDIUM, LOW, DELETE}, mapped from the above as:
  - HIGH: `slop_score ≤ 3` and both flags true,
  - MEDIUM: `4 ≤ slop_score ≤ 6`,
  - LOW: `7 ≤ slop_score ≤ 8`,
  - DELETE: `slop_score ≥ 9` or either flag false.

The judge is instructed to reject by default when in doubt. The asymmetry justifies this: a false positive (decorative task in the corpus) silently weakens the benchmark; a false negative (real task quarantined) just means we lose one task out of hundreds.

---

## 7. Why two pipelines

Markdown-only PRs do not require an agent to design tests, choose files, or run Docker; the transformation from PR-diff to scaffolded task is mechanical (extract distinctive added lines, grep for them in the agent's output). Routing them through the Opus + sandbox pipeline produced lower-quality tasks — the LLM occasionally invented additional files or paraphrased the diff, breaking the verbatim grep. Pipeline B produces tighter behavioral tests at much lower marginal effort per task, in exchange for one strict asymmetry: the test is verbatim, so a competent agent that paraphrases the gold answer fails. The post-judge rejects PRs where this asymmetry is severe.

For Pipeline A the same logic does not apply: deciding which test to write, where to write it, and how to phrase the instruction so that the agent's path to a fix is non-trivial all require a model strong enough to read the repository structure. We retain Opus there.

---

## 8. Failure modes observed in production

Identified during the 2026-04-27 batch. Each is documented for reproducibility and to clarify why the post-judge is necessary:

- **Auto-bot PRs** (26 of 104 LOW + DELETEs, by repository origin): one repository (PrefectHQ) runs an automated commit-watcher that opens "Update AGENTS.md for commit X" PRs after each push to main. These pass the tier-1 path regex but contain no human-curated content. Pre-judge catches title-level cases; post-judge catches the rest by detecting "Automated AGENTS.md update" in the PR body.
- **Broken-yaml manifests** (33 of 104): a scaffolder bug, identified and fixed mid-run, emitted `eval_manifest.yaml` files with mixed-indent YAML block scalars when the gold patch contained outdented lines. The judge correctly rejected these via `yaml.safe_load` failure.
- **Generic AI-authored skills** and **boilerplate**: a residual set (≈30-50, exact count requires keyword-tag review) of PRs that add net-new SKILL.md files whose bodies are generic prose ("This skill helps with X") with no concrete commands, file paths, or anti-patterns. The task prompt offers nothing the agent could not invent independently, so the verbatim-grep test is unreliable.
- **Self-referential meta-content** (3 of 104): "Add a skill for managing skills" — passes the regex, fails causality.

---

## 9. Yield comparison

| Pipeline | Source PRs | Final corpus | Per-PR yield |
|---|---|---|---|
| A — Code-fix (single 2026-04-26 pass) | 19,417 | ≈540 (this pass; cumulative `harbor_tasks/` is 582) | ≈2.8% |
| B — Markdown-authoring (single 2026-04-27 batch) | 9,629 | 214 new (cumulative `harbor_tasks_md_authoring/` is 718) | ≈2.2% (new) / 7.5% (with re-validated pre-existing) |

Pipeline B's path-regex pre-filter extracts a much narrower starting population, so its absolute count of new tasks is lower per pass; the pre-filter does most of the selection work before any LLM is invoked.

---

## 10. Reproducibility

Per-row decision logs are checked into the repository for the 2026-04-27 batch:

- `scouted_scaleup_v2_prejudged.decisions.csv`, `scouted_round2_v2_prejudged.decisions.csv` — pre-judge decisions for every PR considered, with verdict and ≤ 12-word reason.
- `pipeline_logs/scaffold_v4_2026_04_26/md_quality_v2_combined.json` — post-judge verdicts for every scaffolded task with the full structured output (`load_bearing`, `research_relevant`, `slop_score`, `evidence`, `verdict`).

All Gemini calls use temperature 0.1, structured output via `responseMimeType: "application/json"` + `responseSchema`, and a thinking budget of 256 tokens.

---

## 11. Limitations

- **Verbatim-grep tests** in Pipeline B reward agents that produce exactly the gold prose. A competent agent that produces semantically equivalent but textually different content fails. Mitigated by the post-judge, not eliminated.
- **Single-classifier post-judge** in Pipeline B. We do not currently run a second-classifier cross-check, in contrast to Pipeline A which historically used a Kimi → Gemini → Kimi cross-validation loop.
- **Recency window asymmetry**. Pipeline A uses 12 months, Pipeline B uses 24. Comparisons of yield rates across the two pipelines are not strictly apples-to-apples.
- **Auto-fallback path** during Gemini 3.1 Pro Flex tier outages. The Flex tier returned 503 UNAVAILABLE for sustained periods on 2026-04-27; the pipeline's auto-fallback to Standard tier restored throughput.
- **Tier-1 file definition is closed**. Any new agent-instruction file format (e.g., a future `.codex/agents/*.md` convention) must be added to the regex by hand before it is recognized.
