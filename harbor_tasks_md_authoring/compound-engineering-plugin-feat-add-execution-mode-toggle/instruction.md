# feat: add execution mode toggle and context pressure bounds to parallel skills

Source: [EveryInc/compound-engineering-plugin#336](https://github.com/EveryInc/compound-engineering-plugin/pull/336)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md`
- `plugins/compound-engineering/skills/resolve-pr-parallel/SKILL.md`
- `plugins/compound-engineering/skills/resolve-todo-parallel/SKILL.md`

## What to add / change

## Summary

Inspired by @Drewx-Design's work in #178, which identified parent context overflow as a real problem in the original `deepen-plan` and solved it with a full file-based map-reduce architecture. That approach is well-suited to the stable `deepen-plan` skill, which runs 13-26+ agents against every section of a plan.

`deepen-plan-beta` takes a fundamentally different approach — it scores sections by risk and only deepens the weakest 2-5, using at most ~8 targeted agents total. Because of that smaller scope, the full map-reduce pipeline from #178 would be overengineered here. But the core insight — that unbounded agent returns can overwhelm the parent context — still applies, especially on high-risk plans where even a few agents produce bulky source-backed analysis.

This PR adds a lightweight version of that idea: a direct/artifact-backed execution mode toggle. Direct mode (inline returns) is the default for the common case. Artifact-backed mode activates only when the research scope is large enough to justify scratch files — 5+ agents returning meaningful findings, long section excerpts, or high-risk topics. The same pattern is applied to `resolve-pr-parallel` and `resolve-todo-parallel`, which had the same unbounded-return problem with large item sets.

### Changes

- **`deepen-plan-beta`**: Adds execution mode toggle with clear escalation signals and a mid-run escape hatch if direct mode starts bloating
- **`resolve-pr-parallel` and `resolve-todo-parallel`**: Adds

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
