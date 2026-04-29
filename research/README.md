# Research

Research notes, postmortems, and design docs for the agentsmd-rl benchmark.
Grouped by topic. Dated planning logs and superseded proposals live in
[`archive/`](./archive/).

> **Start here**: [`data_mining_pipeline.md`](./data_mining_pipeline.md) is the
> canonical methods doc — how we mine PRs, what each filter checks for, and
> the per-stage funnel diagrams (Mermaid) for each of the two parts of the
> benchmark. Snapshot 2026-04-28: **3,172 active tasks** (2,482 in Part 2,
> 609 in Part 1, 81 in the hybrid corpus).

## Index

### Corpus construction

- [**data_mining_pipeline.md**](./data_mining_pipeline.md) *(canonical)* —
  How merged GitHub PRs become benchmark tasks. The two parts —
  agentmd-following (Part 1, 609 tasks) and agentmd-create/edit (Part 2,
  2,482 tasks) — with Mermaid funnel diagrams, a stage-by-stage table of
  what each filter checks, and the failure-mode catalog observed in
  production. Includes the 2026-04-28 comprehensive scout (24 code-search
  queries + 28 date-windowed title queries → 6,966 unique candidate PRs →
  1,351 newly-built tasks).
- [**scaffold-gates-design.md**](./scaffold-gates-design.md) — Quality-gate
  proposals for the scaffold step (taskforge/task_lint.py). Changes 1 & 4
  shipped; 2/3/5 on the roadmap.

### Test quality & oracles

- [**towards-better-tests.md**](./towards-better-tests.md) — Why
  test-rewriting is a frontier-model task. DeepSeek produced 0/22
  genuine rewrites across 646 tasks; DeepSeek and DeepSeek produced 2/3.
  Merges the earlier `test-design-audit.md` (archived) with the April 2026
  experimental validation.

### Rubric pipeline

- [**rubric-reward-postmortem.md**](./rubric-reward-postmortem.md) —
  Decision record: why LLM-generated rubrics failed as reward signal.
  Binary test outcome is the sole reward; rubrics are monitoring-only.
  *(Supersedes the earlier `rubric-audit-findings.md`, now in archive.)*

### Benchmark integrity

- [**agent-manifest-confounding.md**](./agent-manifest-confounding.md) —
  Dataset audit: recent PR-mined SWE benchmarks implicitly include tasks
  from repos with agent instruction files, introducing unmeasured
  confounders.
- [**reward-tampering-in-scaffold-agents.md**](./reward-tampering-in-scaffold-agents.md) —
  Incident report: 8/804 LLM validate-agents edited eval rubric files to
  force `pass=true` via jailbreak injection. Emergent reward hacking from
  base-model reasoning alone, no RL training. Mitigations live in
  `taskforge/quality_gate.py`.

### Reference

- [**grading-schema-comparison.md**](./grading-schema-comparison.md) —
  Reference: comparison of 8 eval frameworks (Anthropic, Harbor, SWE-bench,
  METR, Inspect, Vivaria, SWE-RM, AgentBench). Note: our shipped scorer is
  simpler (binary outcome per CLAUDE.md), so the recommended unified schema
  here is partially superseded — kept for the framework comparison.
- [**trajectory-logging-design.md**](./trajectory-logging-design.md) —
  ATIF schema v1.6 conversion, W&B integration, harbor-view compatibility.
  Blueprint for the trajectory-logging side of `claude-code-rl-w-tinker/`.

## Archive

Documents in `archive/` are dated planning logs, run logs, or proposals
superseded by later decisions. Kept for historical context:

- `scouting_report_2026_04_26.md` — Single-day Part-1 scout pass
  (19,417 PRs → 13,046 judged → 750 wins). The numbers were absorbed into
  `data_mining_pipeline.md` §Part 1; the per-day report is preserved here
  for the per-repo yield breakdown and classifier comparisons.
- `rubric-audit-findings.md` — Mar-29 audit of 106 task rubrics; the
  taxonomy of errors fed into `rubric-reward-postmortem.md`'s decision to
  drop rubrics from the reward signal.
- `0408_plan.md`, `04_05_overnight_glm_scaffold.md` — Overnight run logs
  from specific dates.
- `mvp-roadmap.md` — Early philosophical roadmap.
- `negative_rubrics_plan.md` — Distractor-rubric plan; predated the
  rubric-reward postmortem's outcome-only decision.
- `test-design-audit.md` — March 2026 test-quality audit; merged into
  `towards-better-tests.md`.
- `pipeline-v2-plan.md` — Mar-30 v2-migration plan; superseded by the
  current architecture (eval_manifest v2.0 schema and 4-track eval are
  live; the named scripts in this plan were never built as proposed).
- `benchmark_construction_log.md` — Apr-1-3 v2-migration sprint log;
  corpus has since grown well past the snapshot here.
- `dag_architecture.md` — Apr-8 reactive self-healing DAG proposal;
  current pipeline is the simpler `taskforge/pipeline.py` parallel
  orchestrator with quarantine + DeepSeek rescue.
- `e2b_validation_plan.md` — Apr-8 plan for the harbor-worker E2B template;
  shipped as `taskforge/e2b.py` and `scripts/run_agent_eval.py --env e2b`.
- `tinker-experiment-log-2026-03-29.md` — Early E2B/Nemotron-120B GRPO
  training-run log; key lessons (E2B cleanup, permission fixes, cost) have
  been absorbed into MEMORY.md feedback notes.

## How to add a new doc

1. Use lowercase-hyphen-kebab filename: `new-topic-name.md`.
2. Start with a dated YAML-ish header or first-line date tag so readers
   know when it was written.
3. Add an entry to the index above under the most appropriate group.
4. If it supersedes or merges an existing doc, move the old doc to
   `archive/` and note the supersession in both docs.
5. Prefer concrete evidence (code snippets, numbers) over speculation.
   Every claim should be traceable to a log, commit, or external link.
