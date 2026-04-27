# Data Construction Methods

This document specifies how we mine merged GitHub PRs and convert them into runnable benchmark tasks. The protocol produces two complementary corpora: code-fix tasks and markdown-authoring tasks. Both are released with pre-built Docker images.

**Current corpus** (snapshot 2026-04-27):

| Corpus | Active tasks | Diff content tested | Scaffold method | Quality gate |
|---|---|---|---|---|
| `harbor_tasks/` | 585 | Code change that depends on a documented rule | Claude Opus 4.7 in an isolated sandbox | Docker oracle (build, run, expect reward 0/1) + LLM rubric judge |
| `harbor_tasks_md_authoring/` | 718 (706 HIGH + 12 MEDIUM) | Edits to agent-instruction files only | Deterministic transform — no LLM | Two-stage Gemini 3.1 Pro judge |

Both corpora ship as images on `ghcr.io/findalexli/agentsmd-rl/<task>:latest`. Combined: **1,303 active tasks**.

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
| Markdown-authoring corpus, batch 2026-04-27 | 24 months | 1,042 |

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
| Markdown-authoring (2026-04-27 batch) | 1,042 | ≈67,400 | 9,629 |

The 14,549 → 13,046 transition in the code pipeline is a slug-deduplication against the cumulative baseline corpus (existing `(repo, pr)` pairs are skipped).

---

## 4. Pipeline A — Code-fix tasks

The expensive pipeline. Each surviving PR receives a Gemini 3.1 Pro causality classification, then (for class A or B) a single Claude Opus 4.7 call inside an isolated sandbox produces the runnable task. Numbers below are for the **2026-04-26 scout pass**; the cumulative `harbor_tasks/` corpus is the result of multiple such passes accumulated over weeks.

| Stage | Mechanism | Input | Drop | Output |
|---|---|---|---|---|
| 4.1 Slug deduplication | Drop PRs already represented in the baseline (4,809 stubs); key on slug + `(repo, pr)` | 19,417 | 4,868 | 14,549 |
| 4.2 Tier-1 repo allowlist | Drop PRs from repositories with no confirmed tier-1 file | 14,549 | 1,503 | 13,046 |
| 4.3 Causality judge | Gemini 3.1 Pro classifier emitting one of {A, B, C, D, ERR} | 13,046 | 12,294 (C+D+ERR) | A=204, B=546, total = **750** |
| 4.4 Opus scaffold + Docker oracle | One-shot Claude Opus 4.7 call inside an E2B sandbox: clone repo, apply gold patch, generate `instruction.md` / `solve.sh` / `tests/test.sh` / `eval_manifest.yaml`, validate via Docker oracle | 750 | ≈25-30% scaffold-fail | ≈530-560 valid |
| 4.5 Quality gate | LLM rubric audit (post-scaffold); tier-A/B failures moved to quarantine | ≈540 | small | merged into the cumulative corpus |

**Cumulative corpus**: 585 active tasks in `harbor_tasks/` (as of 2026-04-27), 92.5% Docker-oracle pass rate (541 pass / 41 fail / 3 missing oracle status).

**End-to-end yield (single pass)**: ≈540 / 19,417 ≈ 2.8%.

The dominant filter is the **causality judge** (stage 4.3): without it, ≈94% of admitted PRs are class C (decorative) — a benchmark constructed from those would be silent on whether the agent attended to the rule files, which is the failure mode the inclusion criterion is designed to prevent.

Aggregate Anthropic API spend across multiple scout-and-scaffold cycles producing the 585-task corpus is on the order of **$1,500-$3,750**, dominated by stage 4.4 at $2-5 per scaffold attempt.

---

## 5. Pipeline B — Markdown-authoring tasks

The cheap pipeline. A regex pre-filter routes only PRs whose every changed file is a tier-1 instruction file; those go through a two-stage Gemini quality gate around a deterministic scaffolder (no LLM in the scaffold step). All numbers below are for the **2026-04-27 batch** in isolation.

| Stage | Mechanism | Input | Drop | Output |
|---|---|---|---|---|
| 5.1 Tier-1 path regex | A PR survives iff every changed path matches the tier-1 regex; codebearing PRs are routed to a separate queue (retained for future Pipeline A processing — currently 34,358 rows total across all scouts to date) | 9,629 | 9,308 | **321** pure-tier-1 PRs (3.3%) |
| 5.2 Pre-judge | Gemini 3.1 Pro Standard tier with input restricted to `{repo, title, file_paths}` (no PR body, no patch). Drops obvious slop only: bot-generated titles ("Automated AGENTS.md update for commit ABC"), test/CI scaffolding, version-bump titles, generic boilerplate. Conservative — defaults to KEEP. | 321 | 19 | **302** (94.1% pass) |
| 5.3 Deterministic scaffold | Per surviving PR: shallow-clone the repo at the base SHA (`git fetch --depth=1`), generate a Dockerfile, write a `solve.sh` that applies the gold patch verbatim, generate `tests/test_outputs.py` with one assertion per *distinctive* added line (top-N longest `+` lines from the diff, ≥ 12 chars, non-trivial alphanumeric content). No LLM call. ≈99% scaffold success per attempt. | 302 | 88 idempotent dupes against the existing corpus | 214 newly-scaffolded tasks |
| 5.4 Post-judge | Gemini 3.1 Pro Standard tier, full context: complete `instruction.md` + complete gold patch. Verdict in {HIGH, MEDIUM, LOW, DELETE} with structured fields for `load_bearing` (boolean), `research_relevant` (boolean), `slop_score` ∈ [0, 10], `evidence` (a quoted phrase from the diff). Run on the full 822-task corpus state at this point (608 pre-existing + 214 newly scaffolded). | 822 | 104 (LOW + DELETE) | HIGH=706, MEDIUM=12, LOW=2, DELETE=102 |
| 5.5 Quarantine | Move LOW + DELETE to `harbor_tasks_md_authoring_quarantine_quality/` | 822 | 104 | **718 active** |

**End-to-end yield (single batch)**: 214 new tasks scaffolded / 9,629 candidates ≈ 2.2%; counting all post-judge survivors (including the 504 pre-existing tasks the judge re-validated as HIGH/MEDIUM): 718 / 9,629 ≈ 7.5%.

The dominant filter is the **path regex** (stage 5.1) at 96.7% drop. The two LLM judges combined contribute another ≈12.4% relative reduction, almost entirely from the **post-judge** — the pre-judge by construction sees no patch content and is limited to title-level signals.

Aggregate Gemini API spend for the 2026-04-27 batch is approximately **$10-20** (≈1,700 calls × ≈$0.005-0.01 per call at Standard tier with structured-output thinking budget).

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

The judge is instructed to reject by default when in doubt. Cost asymmetry justifies this: a false positive (decorative task in the corpus) silently weakens the benchmark; a false negative (real task quarantined) just means we lose one task out of hundreds.

---

## 7. Why two pipelines

Markdown-only PRs do not require an agent to design tests, choose files, or run Docker; the transformation from PR-diff to scaffolded task is mechanical (extract distinctive added lines, grep for them in the agent's output). Routing them through the Opus + sandbox pipeline produced lower-quality tasks — the LLM occasionally invented additional files or paraphrased the diff, breaking the verbatim grep. Pipeline B is roughly **100-200× cheaper per task** than Pipeline A and produces tighter behavioral tests, in exchange for one strict asymmetry: the test is verbatim, so a competent agent that paraphrases the gold answer fails. The post-judge rejects PRs where this asymmetry is severe.

For Pipeline A the same logic does not apply: deciding which test to write, where to write it, and how to phrase the instruction so that the agent's path to a fix is non-trivial all require a model strong enough to read the repository structure. We retain Opus there.

---

## 8. Failure modes observed in production

Identified during the 2026-04-27 batch. Each is documented for reproducibility and to clarify why the post-judge is necessary:

- **Auto-bot PRs** (≈26 of 102 DELETEs): one repository (PrefectHQ) runs an automated commit-watcher that opens "Update AGENTS.md for commit X" PRs after each push to main. These pass the tier-1 path regex but contain no human-curated content. Pre-judge catches title-level cases; post-judge catches the rest by detecting "Automated AGENTS.md update" in the PR body.
- **Generic AI-authored skills** (≈30 of 102 DELETEs): PRs adding net-new SKILL.md files where the body is generic prose ("This skill helps with X") with no concrete commands, file paths, or anti-patterns. Often impossible to scaffold meaningfully because the task prompt has nothing the agent could not invent independently.
- **Broken-yaml manifests** (31 of 102 DELETEs): a scaffolder bug, identified and fixed mid-run, emitted `eval_manifest.yaml` files with mixed-indent YAML block scalars when the gold patch contained outdented lines. The judge correctly rejected these on `yaml.safe_load` failure.
- **Self-referential meta-content** (small count): "Add a skill for managing skills" — passes the regex, fails causality.

---

## 9. Yield comparison

| Pipeline | Source PRs | Final corpus | Per-PR yield | Per-task LLM cost |
|---|---|---|---|---|
| A — Code-fix (single 2026-04-26 pass) | 19,417 | ≈540 (this pass; cumulative `harbor_tasks/` is 585) | ≈2.8% | $2-5 |
| B — Markdown-authoring (single 2026-04-27 batch) | 9,629 | 214 new (cumulative `harbor_tasks_md_authoring/` is 718) | ≈2.2% (new) / 7.5% (with re-validated pre-existing) | < $0.01 |

Pipeline B's path-regex pre-filter extracts a much narrower starting population, so its absolute count of new tasks is lower per pass; in cost-per-task terms it is two orders of magnitude cheaper.

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
- **Auto-fallback path** during Gemini 3.1 Pro Flex tier outages. The Flex tier (50% off Standard) returned 503 UNAVAILABLE for sustained periods on 2026-04-27; the pipeline's auto-fallback to Standard tier restored throughput at full price, but cost figures cited above assume Standard tier throughout for safety.
- **Tier-1 file definition is closed**. Any new agent-instruction file format (e.g., a future `.codex/agents/*.md` convention) must be added to the regex by hand before it is recognized.
