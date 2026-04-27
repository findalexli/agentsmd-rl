# feat(ce-plan): add output structure and scope sub-categorization

Source: [EveryInc/compound-engineering-plugin#542](https://github.com/EveryInc/compound-engineering-plugin/pull/542)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-plan/SKILL.md`

## What to add / change

Compared an external plan format against ce:plan output to identify structural ideas worth adopting while preserving the "What not How" philosophy.

Adds two optional elements to the plan template and workflow:

- **Output Structure** — an optional `## Output Structure` section with a file tree for greenfield plans that create new directory hierarchies. Gives reviewers the overall shape at a glance before per-unit details. Explicitly framed as a scope declaration, not a constraint — the implementer may adjust if implementation reveals a better layout. Includes Phase 3.4b guidance with clear when-to-include/skip criteria.

- **Deferred to Separate Tasks** — an optional `### Deferred to Separate Tasks` sub-heading under Scope Boundaries. Distinguishes true non-goals ("won't do") from planned work that will happen in a separate PR, issue, or repo ("doing separately"). Improves project coordination by making follow-up work explicit.

Both additions include corresponding review checklist items in Phase 5.1.

---

[![Compound Engineering](https://img.shields.io/badge/Built_with-Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
![Claude Code](https://img.shields.io/badge/Opus_4.6_(1M)-D97757?logo=claude&logoColor=white)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
