# Agent Manifest Confounding In Recent SWE Benchmarks

Date: 2026-03-28

## Research question

Are post-June-2025 SWE benchmarks implicitly benefiting from repositories that already contain agent guidance files (`AGENTS.md`, `CLAUDE.md`, Copilot instructions)? If so, they partially measure how well an agent exploits prior human scaffolding rather than how well it solves the underlying software problem.

## Hypothesis

> Post-June-2025 SWE datasets may implicitly include tasks from repositories that already had agent instruction files at the time the task was created, introducing an unmeasured confounder.

| # | Sub-hypothesis |
|---|---|
| H1 | Older / manually-curated datasets anchored before the manifest wave: low risk |
| H2 | Recent PR-mined datasets — especially those with 2025 activity: materially higher risk |

## Method

For each benchmark, check (1) data provenance and date range, (2) whether the paper controls for agent files, (3) released metadata with task timestamps, and (4) spot-check task timestamp vs. first introduction of `AGENTS.md` / `CLAUDE.md` in the repo.

## Main finding

The confounder is plausible and probably real for some datasets, but task-level prevalence is not yet established.

> Recent PR-mined SWE datasets with a meaningful 2025 slice can sample from repositories that either had agent manifests at task time or entered that regime shortly afterward. No major benchmark paper checked controls for this.

## Benchmark assessments

| Benchmark | Risk | Time anchor | Why |
|---|---|---|---|
| **SWE-Gym** | Low | Python repos created before 2022-07-01, reduced to 11 repos | Mostly outside the manifest era |
| **SWE-rebench V2** | Moderate | 32,079 tasks, 2014–2025 | Real but small late-2025 slice (627 tasks across 348 repos ≥ 2025-06-01) |
| **SWE-Universe** | High | ~33.3M PRs over 2021–2025, filtered to ~1M; uses 2025 PRs without linked issues | Largest exposure surface, no explicit audit |
| **SWE-Next** | Likely exposed | 3,971 seed repos, 102,582 commit pairs from merged PRs | PR-mined and recent; no audit released |

### SWE-rebench V2 spot checks

We pulled the released HF parquet metadata directly. Three repos in the late slice:

| Repo | Latest task timestamp | Manifest first introduced | Verdict |
|---|---|---|---|
| `GradleUp/shadow` | 2025-09-26 | `AGENTS.md` 2026-02-13 | Task predates manifest |
| `detekt/detekt` | 2025-10-22 | `AGENTS.md` + `CLAUDE.md` 2026-02-03 | Task predates manifests |
| `pandas-dev/pandas` | 2025-07-19 | `AGENTS.md` exists; date not traced | Inconclusive |

Sources: https://arxiv.org/abs/2412.21139 (SWE-Gym), https://arxiv.org/abs/2602.23866 + https://huggingface.co/datasets/nebius/SWE-rebench-V2 (SWE-rebench V2), https://arxiv.org/abs/2602.02361 (SWE-Universe), https://arxiv.org/abs/2603.20691 (SWE-Next).

## Established with confidence

1. SWE-Gym is mostly outside the relevant time regime.
2. SWE-rebench V2 has a real but small post-2025-06-01 slice.
3. Some of those late-slice repos now contain `AGENTS.md` / `CLAUDE.md`.
4. Two checked examples (`GradleUp/shadow`, `detekt/detekt`) added those files *after* the benchmark task dates.
5. SWE-Universe and SWE-Next are structurally more exposed than SWE-Gym.
6. None of the checked benchmark papers explicitly controls for agent instruction files.

## Not yet established

1. Prevalence of tasks where the manifest was already present at task time.
2. Whether agent performance changes when those files are stripped.
3. Whether benchmarks sample repos whose PRs/issues were themselves agent-authored.
4. Whether the effect is concentrated in a few popular repos or broadly distributed.

## Next steps

### Step 1 — Task-time manifest audit

For each `(dataset_instance, repo)` pair, join task timestamp against first-introduction date of `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` (optionally `GEMINI.md`, `.github/instructions/*.instructions.md`). Label each task one of:

```
manifest_preexisting | manifest_added_later | no_manifest_found
```

This is the core audit. Without it, the discussion stays speculative.

### Step 2 — Priority order

```
SWE-Universe  >  SWE-Next  >  SWE-rebench V2 late-2025 slice  >  SWE-bench Live
```

SWE-Gym remains a contrast case.

### Step 3 — Report prevalence, not anecdotes

Per dataset: total fraction with preexisting manifests, fraction post-2025-06-01, fraction in top-100 most-active repos, fraction by language ecosystem.

### Step 4 — Counterfactual evaluation

On the manifest-positive subset, compare agent runs with manifests present vs. removed. Metrics: resolve rate, patch-apply rate, localization quality, tokens / tool calls / runtime cost. This upgrades the work from a dataset audit to a causal benchmark study.

### Step 5 — Extension

If the manifest effect exists, the natural follow-up is whether benchmarks also inherit *agent-authored repository history* (PR descriptions, fixes, tests, discussion text produced with coding agents). Likely co-occurs with manifest presence.

## Proposed claim for memo

> Recent SWE benchmarks do not currently audit for repository-level agent guidance files. While older datasets such as SWE-Gym are largely outside the relevant adoption window, newer PR-mined datasets such as SWE-Universe, SWE-Next, and the late-2025 slice of SWE-rebench V2 are structurally exposed to this confounder. Initial repo-level checks confirm that benchmarked repositories now participate in the agent-manifest ecosystem, though the prevalence of tasks that postdate manifest introduction remains to be measured.

## Practical takeaway

Not another literature pass — a timestamped repository audit. The decisive test:

> Did the repository already contain an agent instruction file when the benchmark task was created?

That single join converts the concern from plausible to measurable.
