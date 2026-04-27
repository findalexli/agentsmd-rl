# feat(ce-plan): add interactive deepening mode for on-demand plan strengthening

Source: [EveryInc/compound-engineering-plugin#443](https://github.com/EveryInc/compound-engineering-plugin/pull/443)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-plan/SKILL.md`

## What to add / change

## Summary

When the `deepen-plan` command was folded into `ce:plan`, the ability to review sub-agent findings individually before they modified the plan was lost. Users working on complex multi-phase projects want to accept or reject each reviewer's suggestions rather than having them auto-integrated.

This adds an **interactive deepening mode** that activates when a user explicitly asks to deepen an existing plan (e.g., "deepen the plan", `/ce:plan deepen`). Auto-deepening during plan generation is unchanged.

Fixes #429

## What changed

- **Skill description and argument-hint** updated so ce:plan auto-triggers for deepening requests
- **Phase 0.1** — deepen intent now targets plan docs (not requirements docs), with light-touch discovery that confirms with the user when the match isn't obvious
- **Phase 5.3** — two deepening modes: auto (default during generation, unchanged) and interactive (on-demand, per-agent accept/reject/discuss review)
- **New Phase 5.3.6b** — interactive finding review gate between agent dispatch and synthesis. Findings presented one agent at a time; only accepted findings are integrated
- **Phase 5.3.7** — interactive mode only synthesizes accepted findings
- **Pipeline mode** — always auto, no behavioral change for automated workflows
- **Signal word tightening** — only "deepen"/"deepening" auto-enter the fast path. Generic words like "strengthen", "confidence", "gaps" require user confirmation when targeting the whole plan, and ro

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
