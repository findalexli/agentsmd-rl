# Data Construction: Two Pipelines for Mining Agent-Instruction-Aware PR Tasks

**Snapshot 2026-04-27.** This document specifies the construction protocol for `agentsmd-rl`, an SWE-style benchmark testing whether a coding agent attends to project-specific rule files (`CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `.cursor/rules/*`). We mine merged PRs from public GitHub repositories and convert each survivor into a runnable benchmark task with a behavioral test. Two pipelines run in parallel, distinguished by what the gold diff modifies and how expensive the resulting task is to scaffold.

| Corpus | Active tasks | Diff content | Per-task scaffold cost | Quality gate |
|---|---|---|---|---|
| `harbor_tasks/` | 585 | Code (with rules informing the fix) | $2-5 (Claude Opus 4.7 in E2B) | Docker oracle + rubric LLM judge |
| `harbor_tasks_md_authoring/` | 718 (706 H + 12 M) | Tier-1 instruction files only | <$0.01 (deterministic, no LLM) | Gemini Standard pre-judge + post-judge |

Both corpora are published as runnable Docker images on `ghcr.io/findalexli/agentsmd-rl/<task>:latest`. Total: **1,303 active tasks**.

## 1. Inclusion criterion

A merged PR enters the benchmark only when its gold fix is *causally shaped by the agent-instruction surface*: the diff would have looked materially different if the repository's tier-1 instruction files had been absent. Three classes follow:

- **Type A** — the diff modifies a tier-1 instruction file. The agent's task is to write the instruction text correctly.
- **Type B** — the diff is code-only, but the choice of fix encodes a rule documented in the repo's tier-1 files (e.g., "use 7-character commit hashes in dependency declarations", "no wildcard imports in TypeScript modules"). Type B is the dominant bucket conceptually: most agent-instruction following manifests in code, not in markdown.
- **Type C** — decorative. The fix is determined by the bug alone; removing the markdown would not change a single character. Excluded.

We also exclude PRs that are mechanically unscaffoldable as a Linux Docker benchmark (Type D): platform-specific runtimes (iOS/Android/Windows-only), GPU/CUDA dependencies, multi-thousand-line cross-cutting refactors, no testable behavior.

The two pipelines specialize on Type A (markdown_authoring) and the union of Type A+B (code-fix), with the unscaffoldable Type D dropped at classification time.

## 2. Repository discovery

Both pipelines share a single discovery step. We query `gh search repos` across thirteen agent-instruction-related topics (`claude-code`, `claude-skills`, `agent-skills`, `agents-md`, `claude-md`, `cursor-rules`, `awesome-claude-*`, `claude-plugins`, `claude-code-skill`, `agent-instructions`) and three repository-content paths (`SKILL.md in:path`, `.claude/skills in:path`, `.cursor/rules in:path`). Each query is sorted by stars; the top 200–300 results are aggregated. We retain only repositories with ≥5 stars to exclude empty or abandoned projects, and deduplicate against repositories scouted in earlier passes via a persistent allowlist.

| Run | Window | Unique repos retained |
|---|---|---|
| Code-fix corpus (cumulative through 2026-04-26) | 12 months | 147 |
| Markdown-authoring corpus (single batch 2026-04-27) | 24 months | 1,042 |

The markdown-authoring run uses a longer recency window and broader topic set because per-repo yield of pure-tier-1-path PRs is roughly half that of any-causality PRs (≈3% vs ≈6%); we compensate with breadth.

## 3. Per-repo PR enumeration

For each retained repository we issue `gh pr list --state merged --json files,…` capped at 200 PRs per call (above 200, GraphQL gateway returns 504 on heavy repositories). The `files` field returns each PR's full path list at scout time, eliminating ~50× of subsequent REST `/files` calls in the markdown pipeline.

Per-PR scout-time exclusions:

- `changedFiles ∉ [1, 8]` — multi-file refactors are not clean benchmarks.
- `additions + deletions ∉ [5, 500]` — too small to be testable, too large to be tractable.
- Carrying labels in `{wontfix, dependencies, automated-update, no-changelog}`.
- Older than the recency window.
- Failing a tier-1 exemption test: a PR is dropped as `docs_only` if every changed file is documentation *unless* every changed file matches the tier-1 regex (preserving pure-instruction-file PRs for the markdown pipeline).

| Pipeline | Repos | Raw PRs fetched | Candidates after scout filters |
|---|---|---|---|
| Code-fix | 107 | 19,417 | 14,549 |
| Markdown-authoring | 1,042 | ≈67,400 | 9,629 |

## 4. Pipeline A: Code-fix tasks (`harbor_tasks/`)

Filter rates through 2026-04-26.

| Stage | Mechanism | Drop | Survivors |
|---|---|---|---|
| 4.1 Slug deduplication | Drop PRs already in baseline (slug + (repo, pr) key) | 4,868 | 14,549 → 9,681 |
| 4.2 Tier-1 repo allowlist | Drop PRs from repos with no confirmed tier-1 file | 1,503 | → 13,046 |
| 4.3 Causality classification | Gemini 3.1 Pro per-PR classifier emitting one of `{A, B, C, D, ERR}` | — | 13,046 judged |
|  &nbsp;&nbsp; A (PR edits tier-1 file) | | | 204 (1.6%) |
|  &nbsp;&nbsp; B (code follows a documented rule) | | | 546 (4.2%) |
|  &nbsp;&nbsp; C (decorative; bug fix independent of rules) | dropped | 10,398 | 79.7% rejected |
|  &nbsp;&nbsp; D (platform/GPU/refactor/no-testable-behavior) | dropped | 1,896 | 14.5% rejected |
| 4.4 One-call scaffold | Claude Opus 4.7 in E2B sandbox: clone repo, apply gold patch, generate `instruction.md` + `solve.sh` + `tests/test.sh` + `eval_manifest.yaml`, then validate via Docker oracle (`nop=0, gold=1`) | ≈30% | A+B = 750 → ≈600 valid |
| 4.5 Quality gate | LLM rubric audit (tier-A/B failures moved to quarantine) | small | **585 active** |

**End-to-end yield**: 585 / 19,417 ≈ 3.0%. Aggregate Anthropic API spend for the corpus was on the order of $1,500-$3,750 across ≈750 scaffold attempts; per-task post-quarantine cost is meaningfully higher than the per-attempt cost due to scaffold failures and retries.

The dominant filter is the causality judge (stage 4.3). Without it the surviving pool is ≈94% Type C, and a benchmark constructed from it would be silent on whether the agent attended to the rules — exactly the failure mode the inclusion criterion is designed to prevent.

## 5. Pipeline B: Markdown-authoring tasks (`harbor_tasks_md_authoring/`)

Single batch run 2026-04-27.

| Stage | Mechanism | Drop | Survivors |
|---|---|---|---|
| 5.1 Tier-1 path regex | A PR survives only if every changed file matches the tier-1 regex covering `CLAUDE.md`, `AGENTS.md`, `SKILL.md`, `CONVENTIONS.md`, `.cursorrules`, `.windsurfrules`, `.clinerules`, `.continuerules`, `.claude/{rules,skills,agents}/*.md`, `.cursor/rules/*`, `.github/{copilot-instructions.md, skills/*/SKILL.md, prompts/*.prompt.md}`, `.{agents,opencode,codex}/skills/*/SKILL.md`, `.mdc`. PRs touching any non-matching path are routed to a separate codebearing queue (≈31K rows, retained for future Pipeline A processing). | 9,308 | 9,629 → 321 |
| 5.2 Pre-judge | Gemini 3.1 Pro Standard tier, structured-output classifier with input restricted to `{repo, title, file_paths}` (no PR body, no patch). Drops obvious slop only: bot-generated titles ("Automated AGENTS.md update for commit ABC"), test/CI scaffolding ("test: broken merge-batch e2e PR"), pure version-bump or metadata-only titles, generic boilerplate ("Add comprehensive guide for X"). Conservative — defaults to `KEEP`. | 19 | → 302 |
| 5.3 Deterministic scaffold | Per surviving PR: shallow-clone the repo at the base SHA, generate a Dockerfile using `git fetch --depth=1`, write a `solve.sh` that applies the gold patch verbatim, generate `tests/test_outputs.py` containing one assertion per *distinctive* added line (top-N longest lines from the PR's `+` content, deduplicated, length ≥ 12 characters, non-trivial alphanumeric content). No LLM call. ≈99% scaffold success. | small | 214 newly scaffolded (the remainder were idempotent matches against tasks already in the corpus from prior scouts) |
| 5.4 Post-judge | Gemini 3.1 Pro Standard tier with full context: complete `instruction.md` + complete gold patch. Verdict in `{HIGH, MEDIUM, LOW, DELETE}` with structured fields for `load_bearing` (boolean), `research_relevant` (boolean), `slop_score` ∈ [0,10], `evidence` (a quoted phrase from the diff). Across all 822 v2-scaffolded tasks: HIGH=706 (85.9%), MEDIUM=12 (1.5%), LOW=2 (0.2%), DELETE=102 (12.4%). | — | 822 judged |
| 5.5 Auto-quarantine | LOW + DELETE moved to `harbor_tasks_md_authoring_quarantine_quality/` | 104 | **718 active** |

**End-to-end yield**: 718 / 9,629 ≈ 7.5%. Aggregate Gemini API spend for the entire 2026-04-27 batch was approximately $50, dominated by the post-judge stage. The pre-judge stage is roughly free (321 calls at Standard tier ≈ $1.6).

The dominant filter is the path regex (stage 5.1) at 96.7% drop. The two LLM judges combined contribute another ≈12.4% relative reduction, almost entirely from the post-judge — the pre-judge by construction sees no patch content and is limited to title-level signals.

## 6. Quality gate criteria (markdown-authoring)

The post-judge prompt instantiates the inclusion criterion as four operational definitions:

- **load_bearing**: would an agent reading vs. ignoring this gold patch produce different downstream code? Falsified by generic prose, self-referential meta-content, pure formatting changes, lockfile-style updates, frontmatter-only PRs.
- **research_relevant**: does the PR fit the agent-md research schema? Falsified when the file is technically tier-1 but the change carries no behavioral assertion an agent could either follow or violate.
- **slop_score** ∈ [0, 10]: 0 = concrete commands, file paths, version pins, anti-pattern rules; 10 = AI-generated boilerplate, auto-bot output, content any LLM could produce without context.
- **verdict** ∈ {HIGH, MEDIUM, LOW, DELETE}: HIGH = `slop_score ≤ 3` and both flags true; MEDIUM = `4 ≤ slop_score ≤ 6`; LOW = `7 ≤ slop_score ≤ 8`; DELETE = `slop_score ≥ 9` or either flag false.

The judge is instructed to reject by default when in doubt (`slop_score ≥ 6`). The asymmetric thresholds reflect the cost asymmetry: a false positive (decorative task in the corpus) silently weakens the benchmark; a false negative (real task quarantined) just means we lose one task out of hundreds.

## 7. Why two pipelines

Markdown-only PRs do not require an agent to design tests, choose files, or run Docker. The transformation from PR-diff to scaffolded task is mechanical: extract distinctive added lines, grep for them in the agent's output. We previously routed these through Pipeline A (Opus + E2B) at $2-5/task and observed that the resulting tasks were lower quality, not higher: the LLM scaffold sometimes invented additional files or paraphrased the diff, breaking the verbatim grep. Pipeline B is both 100-200× cheaper and produces tighter behavioral tests, at the cost of one strict asymmetry: the test is verbatim, so a competent agent that paraphrases the gold answer fails. The quality gate (stage 5.4) is the workaround — it rejects PRs where verbatim grep is unreasonable as an evaluation.

For Pipeline A the same logic does not apply: deciding which test to write, where to write it, and how to phrase the instruction so the agent's path to a fix is non-trivial all require a model strong enough to read the repository structure. We retain Opus there.

## 8. Failure modes observed in production

We catalog these for reproducibility; each was identified in the 2026-04-27 batch.

- **Auto-bot PRs** (≈26 of 102 DELETEs): PrefectHQ runs an automated commit-watcher that opens "Update AGENTS.md for commit X" PRs after each push to main. These pass the tier-1 path regex but contain no human-curated content. Pre-judge (5.2) catches title-level cases; post-judge (5.4) catches the rest by detecting "Automated AGENTS.md update" in `instruction.md`.
- **Generic AI-authored skills** (≈30 of 102 DELETEs): PRs adding net-new SKILL.md files where the body is generic prose ("This skill helps with X") with no concrete commands, file paths, or anti-patterns. Often impossible to scaffold meaningfully because the task prompt has nothing the agent could not invent independently.
- **Broken-yaml manifests** (31 of 102 DELETEs in this batch): a scaffolder bug (since fixed) emitted `eval_manifest.yaml` files with mixed-indent YAML block scalars when the gold patch contained outdented lines. The judge correctly rejected these as DELETE on `yaml.safe_load` failure.
- **Self-referential meta-content** (small count): "Add a skill for managing skills" — passes regex, fails causality.
- **Polluted tasks**: a single legacy task in `harbor_tasks/` (`airflow-openlineage-dagrun-partition-fields`) had the entire airflow source tree dumped into its task directory by a malformed scaffold. Detected via the pre-commit secret-scan hook (Stripe doc example matched the regex). Excluded from the latest commit.

## 9. Yield summary

| Pipeline | Source PRs | Final corpus | Per-PR yield | Per-task LLM cost |
|---|---|---|---|---|
| Code-fix (Pipeline A) | 19,417 | 585 | 3.0% | $2-5 |
| Markdown-authoring (Pipeline B) | 9,629 | 718 | 7.5% | <$0.01 |

Pipeline B's higher yield reflects a stricter pre-filter: the path regex is extracting precisely the population for which the deterministic transform is valid, whereas Pipeline A's pre-filter (repo allowlist) admits a much broader population that the LLM judge then prunes.

## 10. Reproducibility

The pipeline is implemented in `taskforge/scout.py` (discovery + scout), `scripts/scaffold_markdown_only.py` (markdown-authoring scaffold), `taskforge/e2b_worker.py` (code-fix scaffold), and `scripts/quality_judge.py` (Gemini pre- and post-judge). Each Gemini call uses temperature 0.1, structured output via `responseMimeType: "application/json"` + `responseSchema`, and a thinking budget of 256 tokens. The scout repos list, the prompt templates, and a row-level audit CSV (`scouted_*_v2_prejudged.decisions.csv`, `pipeline_logs/scaffold_v4_2026_04_26/md_quality_v2_combined.json`) are checked into the repository for the 2026-04-27 batch.

## 11. Limitations

- **Verbatim-grep tests** in Pipeline B reward agents that produce exactly the gold prose. A competent agent that produces semantically equivalent but textually different content fails. Mitigated by quality-gate rejection of PRs where this asymmetry is severe; not eliminated.
- **Single-judge classifier**. We do not currently run a second-classifier cross-check on Pipeline B's post-judge. Pipeline A historically used a Kimi-Gemini cross-validation loop; the markdown corpus does not.
- **Recency window asymmetry**. Pipeline A uses 12 months, Pipeline B uses 24. Comparisons of yield rates between the two pipelines are not strictly apples-to-apples.
- **Gemini Flex availability**. The Flex tier (50% off Standard) was unavailable for sustained periods on 2026-04-27, returning 503 UNAVAILABLE; the pipeline's auto-fallback to Standard restored throughput at full price. Total batch cost is still <$50.
