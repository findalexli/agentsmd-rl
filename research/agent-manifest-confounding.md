# Agent Manifest Confounding In Recent SWE Benchmarks

Date: 2026-03-28

## Research question

Are newer software-engineering benchmarks and training corpora implicitly benefiting from repositories that already contain human-written agent guidance, such as `AGENTS.md`, `CLAUDE.md`, or GitHub Copilot instruction files?

This matters because such files can change the difficulty and structure of repository-level tasks. If they are present at task time, then a benchmark may partially measure how well an agent exploits prior human scaffolding, not just how well it solves the underlying software problem.

## Working hypothesis

The main hypothesis is:

> Post-June-2025 SWE datasets may implicitly include tasks from repositories that already had agent instruction files at the time the task was created, introducing an unmeasured confounder into both benchmark evaluation and post-training.

There are two narrower sub-hypotheses:

1. The risk should be low for older or manually curated datasets whose repository pool is anchored before the current agent-manifest wave.
2. The risk should be materially higher for datasets mined from large volumes of recent GitHub pull requests, especially if they include 2025 repository activity.

## What we checked

We focused on recent or still-relevant benchmark families and ignored pre-June-2025 releases unless they were needed as a contrast case.

We checked:

1. Paper-level data provenance: what repositories or PRs were mined, and from what date range.
2. Whether the paper explicitly controls for `AGENTS.md` / `CLAUDE.md` / Copilot instruction files.
3. Where possible, released dataset metadata with actual task timestamps.
4. Spot checks on concrete repositories to compare:
   - task timestamp in the benchmark dataset
   - first known introduction date of `AGENTS.md` or `CLAUDE.md` in that repository

## Main finding so far

The confounder is plausible and probably real for some recent datasets, but we have not yet shown that it affects a large fraction of tasks.

The strongest current conclusion is:

> New large-scale PR-mined datasets can include repositories that are now in the agent-manifest ecosystem, but our initial repo-level checks suggest that some benchmarked tasks still predate the introduction of those files.

In other words, the risk is clearly present in principle, but the task-level prevalence is not yet established.

## Benchmark-by-benchmark summary

### SWE-Gym

Current assessment: low risk.

Evidence:

- The paper states that the raw repository pool was filtered to Python repositories created before July 1, 2022.
- The executable benchmark itself was then reduced to 11 repositories.
- This makes SWE-Gym mostly a pre-agent-manifest dataset in practice.

Interpretation:

Even if some of those repositories have added agent files by now, SWE-Gym is not mainly a benchmark of recent active repositories from the post-Claude-Code / post-Copilot-agent era.

Bottom line:

SWE-Gym is unlikely to be the main place where this confounder enters.

Source:

- https://arxiv.org/abs/2412.21139

### SWE-rebench V2

Current assessment: moderate risk, but likely limited in magnitude.

Evidence from the paper:

- The paper states that the final dataset contains 32,079 tasks spanning 2014-2025.
- It mines from GitHub Archive and PR histories rather than only fresh issues.

Evidence from the released dataset:

- We directly checked the released Hugging Face parquet metadata.
- `created_at` ranges from 2014-11-10 to 2025-10-31.
- Only 627 of 32,079 tasks occur on or after 2025-06-01.
- Those 627 tasks span 348 repositories.

Interpretation:

SWE-rebench V2 does have a real late-2025 tail, so it can in principle include tasks from repositories that were already agent-instruction-aware. But the dataset is still dominated by older activity, so this is not a dataset-wide explanation for its behavior.

Direct repo spot checks on late-slice repositories:

- `GradleUp/shadow`
  - latest dataset task timestamp we checked: 2025-09-26
  - `AGENTS.md` exists now
  - first introduction of `AGENTS.md`: 2026-02-13
  - implication: checked task predates the manifest
- `detekt/detekt`
  - latest dataset task timestamp we checked: 2025-10-22
  - `AGENTS.md` and `CLAUDE.md` exist now
  - first introduction of both files: 2026-02-03
  - implication: checked task predates the manifests
- `pandas-dev/pandas`
  - latest dataset task timestamp we checked: 2025-07-19
  - `AGENTS.md` exists now
  - first introduction date not yet fully traced in this pass

Bottom line:

SWE-rebench V2 is exposed to the confounder in principle, but the initial checked examples do not yet show tasks that were created after those manifests existed.

Sources:

- https://arxiv.org/abs/2602.23866
- https://huggingface.co/datasets/nebius/SWE-rebench-V2

### SWE-Universe

Current assessment: high-risk candidate for implicit inclusion of agent-prepared repositories.

Evidence:

- The paper states that SWE-Universe harvested about 33.3 million PRs spanning the most recent five years, explicitly 2021-2025.
- It then filtered this to about 1 million high-quality PR candidates.
- It also explicitly mentions using a subset of 2025 PRs without linked issues.

Interpretation:

This is exactly the kind of mining pipeline where the confounder could appear implicitly:

- large PR-mined corpus
- recent 2025 activity
- many active repositories
- no explicit auditing of agent instruction files

What we do not yet have:

- a released task table with per-instance timestamps and repository names that we can audit systematically
- any explicit paper-level control for `AGENTS.md`, `CLAUDE.md`, or Copilot instruction files

Bottom line:

SWE-Universe is currently the strongest candidate for hidden exposure to repository-level agent manifests.

Source:

- https://arxiv.org/abs/2602.02361

### SWE-Next

Current assessment: likely exposed, but not yet audited.

Evidence:

- The paper states that SWE-Next processes 3,971 seed repositories and 102,582 candidate commit pairs mined from real merged PRs.
- The dataset is recent and PR-mined.
- The paper emphasizes repo-quarter profiles and commit-time grouping, but does not mention any audit of agent instruction files.

Interpretation:

Because SWE-Next is built from real merged PRs and is explicitly designed around temporal commit grouping, it is structurally capable of being audited very cleanly. That also means it is structurally capable of carrying this confounder.

What is missing:

- public task-level manifest audit
- repository-level release table sufficient for quick external verification

Bottom line:

SWE-Next should be treated as a likely exposed dataset until proven otherwise.

Source:

- https://arxiv.org/abs/2603.20691

## Current state of the hypothesis

At this point, the hypothesis is not:

> all recent benchmarks are contaminated by agent manifests

The hypothesis is now better stated as:

> recent PR-mined SWE datasets, especially those with a meaningful 2025 slice, are capable of implicitly sampling from repositories that either already had agent manifests at task time or entered that regime shortly afterward; no major benchmark paper we checked appears to control for this factor.

That is already a useful research result, because it identifies a concrete unmeasured variable in benchmark construction.

## What we have established with confidence

1. `SWE-Gym` is mostly outside the relevant time regime.
2. `SWE-rebench V2` includes a real but relatively small post-June-2025 slice.
3. Some repositories in that late slice now do contain `AGENTS.md` and/or `CLAUDE.md`.
4. At least two checked examples (`GradleUp/shadow`, `detekt/detekt`) added those files after the benchmark task dates.
5. `SWE-Universe` and likely `SWE-Next` are much more exposed to this confounder than `SWE-Gym`.
6. None of the checked benchmark papers appears to explicitly control for agent instruction files.

## What we have not established yet

1. The prevalence of tasks where the manifest was already present at task time.
2. Whether performance changes materially when those files are stripped.
3. Whether benchmarks are sampling repositories whose PRs or issues were themselves agent-authored.
4. Whether this effect is concentrated in a small number of popular repositories or broadly distributed.

## Concrete next steps

### Step 1: Build a task-time manifest audit

For each dataset instance, collect:

- repository name
- task timestamp
- task identifier

For each repository, collect:

- first introduction date of `AGENTS.md`
- first introduction date of `CLAUDE.md`
- first introduction date of `.github/copilot-instructions.md`
- optionally `GEMINI.md` and `.github/instructions/*.instructions.md`

Then label each task as one of:

- `manifest_preexisting`
- `manifest_added_later`
- `no_manifest_found`

This is the core audit. Without it, the discussion stays speculative.

### Step 2: Focus on the right benchmark slices

Priority order:

1. `SWE-Universe`
2. `SWE-Next`
3. `SWE-rebench V2` late-2025 slice
4. `SWE-bench Live`

`SWE-Gym` can remain a contrast case rather than the main target.

### Step 3: Report prevalence, not anecdotes

For each dataset, report:

- total fraction of tasks with preexisting manifests
- fraction for tasks after 2025-06-01
- fraction for top-100 most active repositories
- fraction by language ecosystem if available

### Step 4: Run a counterfactual evaluation

Once a manifest-positive task subset is identified, compare:

1. agent runs with manifests present
2. agent runs with manifests removed

Primary metrics:

- resolve rate
- patch apply rate
- localization quality
- tokens / tool calls / runtime cost

This upgrades the work from a dataset audit into a causal benchmark study.

### Step 5: Extend the hypothesis if needed

If the manifest effect exists, a second research question follows naturally:

> Are newer benchmarks also inheriting agent-authored repository history, such as PR descriptions, fixes, tests, or discussion text that were already produced with coding agents?

That is separate from manifest presence, but the two effects likely co-occur in recent active repositories.

## Proposed claim for a paper or memo

A strong but defensible version would be:

> Recent SWE benchmarks do not currently audit for repository-level agent guidance files. While older datasets such as SWE-Gym are largely outside the relevant adoption window, newer PR-mined datasets such as SWE-Universe, SWE-Next, and the late-2025 slice of SWE-rebench V2 are structurally exposed to this confounder. Initial repo-level checks confirm that benchmarked repositories now participate in the agent-manifest ecosystem, though the prevalence of tasks that postdate manifest introduction remains to be measured.

## Practical takeaway

The most important immediate action is not another literature pass. It is a timestamped repository audit.

The decisive test is:

> Did the repository already contain an agent instruction file when the benchmark task was created?

That single join converts the current idea from a plausible concern into a measurable benchmark property.
