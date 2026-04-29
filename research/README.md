# Research

Research notes, postmortems, and design docs for the agentsmd-rl benchmark.
Dated planning logs and superseded proposals live in [`archive/`](./archive/).

> **Start here**: [`data_mining_pipeline.md`](./data_mining_pipeline.md) — how
> we mine PRs into the two corpora, with stage-by-stage funnels and per-task
> file-kind breakdowns. Snapshot 2026-04-28: **3,172 active tasks**
> (2,482 markdown-authoring + 609 markdown-following + 81 hybrid).

## Index

### Corpus construction

- [**data_mining_pipeline.md**](./data_mining_pipeline.md) *(canonical)* —
  How merged GitHub PRs become benchmark tasks. Funnel tables for each part
  and a per-file-kind breakdown of what the 2,482 gold patches actually
  touch.

### Test quality & oracles

- [**towards-better-tests.md**](./towards-better-tests.md) — Why
  test-rewriting is a frontier-model task. MiniMax-M2.7 produced 0/22
  genuine rewrites across 646 tasks; Kimi-K2.6 and GLM-5.1 produced 2/3.

### Rubric pipeline

- [**rubric-reward-postmortem.md**](./rubric-reward-postmortem.md) —
  Decision record: LLM-generated rubrics failed as reward signal. Binary
  test outcome is the sole reward; rubrics are monitoring-only.

### Benchmark integrity

- [**agent-manifest-confounding.md**](./agent-manifest-confounding.md) —
  Dataset audit: recent PR-mined SWE benchmarks implicitly include tasks
  from repos with agent instruction files, introducing unmeasured
  confounders.

### Reference

- [**negative_rubrics_plan.md**](./negative_rubrics_plan.md) — Distractor /
  negative-rubric research plan.

### Decision audit trails (CSV)

- `scouted_round2_v2_prejudged.decisions.csv`
- `scouted_scaleup_v2_prejudged.decisions.csv`
- `md_authoring_quality_judgments.json`

## Archive

Documents in `archive/` are dated planning logs, incident reports, run
logs, or proposals superseded by later decisions:

- `grading-schema-comparison.md` — Survey of 8 eval frameworks. Informed
  early schema decisions; the shipped scorer is binary-outcome per
  CLAUDE.md, much simpler than the recommended unified schema.
- `scaffold-gates-design.md` — Quality-gate design; changes 1 & 4 shipped.
- `reward-tampering-in-scaffold-agents.md` — Incident: 8/804 validate-agents
  edited eval rubric files to force `pass=true`. Mitigations live in
  `taskforge/quality_gate.py`.
- `test_coverage_audit.md` — Static audit snapshot; superseded by
  `towards-better-tests.md`.
- `trajectory-logging-design.md` — ATIF schema v1.6 / W&B integration
  blueprint; ownership moved to Harbor.
- `scouting_report_2026_04_26.md` — Single-day Part-1 scout pass.
- `rubric-audit-findings.md` — Mar-29 rubric taxonomy that fed into the
  rubric-reward postmortem.
- `0408_plan.md`, `04_05_overnight_glm_scaffold.md`,
  `tinker-experiment-log-2026-03-29.md` — Dated overnight / training logs.
- `mvp-roadmap.md`, `dag_architecture.md`, `pipeline-v2-plan.md`,
  `e2b_validation_plan.md` — Early roadmaps and architecture proposals;
  current pipeline is `taskforge/pipeline.py`.
- `benchmark_construction_log.md` — Apr-1-3 v2-migration sprint log.
- `test-design-audit.md` — Merged into `towards-better-tests.md`.

## How to add a new doc

1. Use lowercase-hyphen-kebab filename: `new-topic-name.md`.
2. Start with a dated header so readers know when it was written.
3. Add an entry to the index above under the most appropriate group.
4. If it supersedes an existing doc, move the old one to `archive/`.
5. Prefer concrete evidence (code snippets, numbers) over speculation.
