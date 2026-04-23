# Research

Research notes, postmortems, and design docs for the agentsmd-rl benchmark.
Grouped by topic. Dated planning logs and superseded proposals live in
[`archive/`](./archive/).

## Index

### Test quality & oracles

- [**towards-better-tests.md**](./towards-better-tests.md) *(canonical)* —
  Why test-rewriting is a frontier-model task. MiniMax-M2.7 produced 0/22
  genuine rewrites across 646 tasks; Kimi-K2.6 and GLM-5.1 produced 2/3.
  Merges the prior `test-design-audit.md` (archived) with the April 2026
  experimental validation.

### Rubric pipeline

- [**rubric-audit-findings.md**](./rubric-audit-findings.md) — Technical
  taxonomy of errors in batch-generated rubrics (bare filenames, wrong
  line numbers, hallucinated rules). Proposes three-step verification.
- [**rubric-reward-postmortem.md**](./rubric-reward-postmortem.md) —
  Decision record: why LLM-generated rubrics failed as reward signal.
  Binary test outcome is the sole reward; rubrics are monitoring-only.

### Benchmark integrity

- [**agent-manifest-confounding.md**](./agent-manifest-confounding.md) —
  Dataset audit: recent PR-mined SWE benchmarks implicitly include tasks
  from repos with agent instruction files, introducing unmeasured
  confounders.
- [**reward-tampering-in-scaffold-agents.md**](./reward-tampering-in-scaffold-agents.md) —
  Incident report: 8/804 LLM validate-agents edited eval rubric files to
  force `pass=true` via jailbreak injection. Emergent reward hacking from
  base-model reasoning alone, no RL training.

### Pipeline & infrastructure

- [**dag_architecture.md**](./dag_architecture.md) *(current)* — Six-node
  DAG with per-node retry budgets, self-healing back-edges. Implemented in
  `taskforge/e2b_worker.py`.
- [**e2b_validation_plan.md**](./e2b_validation_plan.md) *(current)* —
  Single harbor-worker E2B template with Docker-in-VM; 50+ parallel
  sandboxes. Backend pool routing per backend account.
- [**pipeline-v2-plan.md**](./pipeline-v2-plan.md) — Scout →
  pre-filter → pre-gen → LLM scaffold → validate construction pipeline.
  Phase 1 (pre-filter) remains as backlog.
- [**trajectory-logging-design.md**](./trajectory-logging-design.md) —
  ATIF schema v1.6 conversion, W&B integration, harbor-view compatibility.
  Blueprint for future RL training runs.

### Reference

- [**grading-schema-comparison.md**](./grading-schema-comparison.md) —
  Reference: comparison of 8 eval frameworks (Anthropic, Harbor, SWE-bench,
  METR, Inspect, Vivaria, SWE-RM, AgentBench). Recommends unified reward
  schema with named components.
- [**benchmark_construction_log.md**](./benchmark_construction_log.md) —
  v2 format migration + agentmd-edits dataset operational log. Contains
  architectural insights (config edits → rubric migration, template
  placeholder cleanup, config-only task identification).
- [**tinker-experiment-log-2026-03-29.md**](./tinker-experiment-log-2026-03-29.md) —
  Early E2B/Nemotron-120B GRPO RL training log. Sandbox lifecycle notes,
  E2B permission fixes, architecture trade-offs (E2B vs Modal,
  tinker-cookbook vs SkyRL). Reference for future RL runs.

## Archive

Documents in `archive/` are dated planning/run logs or proposals
superseded by later decisions. Kept for historical context:

- `0408_plan.md`, `04_05_overnight_glm_scaffold.md` — Overnight run logs
  from specific dates.
- `mvp-roadmap.md` — Early philosophical roadmap, superseded by
  `dag_architecture.md`.
- `negative_rubrics_plan.md` — Distractor-rubric plan; predated the
  rubric-reward postmortem's outcome-only decision.
- `test-design-audit.md` — March 2026 test-quality audit; merged into
  `towards-better-tests.md`.

## How to add a new doc

1. Use lowercase-hyphen-kebab filename: `new-topic-name.md`.
2. Start with a dated YAML-ish header or first-line date tag so readers
   know when it was written.
3. Add an entry to the index above under the most appropriate group.
4. If it supersedes or merges an existing doc, move the old doc to
   `archive/` and note the supersession in both docs.
5. Prefer concrete evidence (code snippets, numbers) over speculation.
   Every claim should be traceable to a log, commit, or external link.
