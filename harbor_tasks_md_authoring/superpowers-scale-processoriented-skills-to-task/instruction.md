# Scale process-oriented skills to task complexity

Source: [obra/superpowers#522](https://github.com/obra/superpowers/pull/522)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/brainstorming/SKILL.md`
- `skills/subagent-driven-development/SKILL.md`
- `skills/writing-plans/SKILL.md`
- `skills/writing-skills/SKILL.md`

## What to add / change

## Summary

- **brainstorming**: Check in with user before transitioning to writing-plans instead of auto-invoking
- **writing-plans**: Structured execution handoff — record context, advise compaction, give exact continuation prompt that adapts based on whether subagents are available
- **subagent-driven-development**: Add scaling paragraph (GATE + orchestrator boundary), graphviz decision diamonds for review elision, check-in before finishing, replace TodoWrite with generic task list language, tighten Red Flags
- All three skills now follow the same pattern: scale effort to task complexity, ask permission before eliding steps, pause at workflow transitions

## Design decisions

- **One paragraph + graphviz + Red Flags** is the minimum viable change for SDD. Graphviz-only (no prose) tested at 7/10 on scaling; the one-paragraph version tests at 10/10.
- **GATE keyword** in prose is what makes agents ask permission rather than deciding unilaterally to skip steps.
- **Orchestrator boundary** ("never implements or reviews code") is enforced via the scaling paragraph and a Red Flags entry — not a standalone section.
- **Subagents cannot spawn sub-subagents** (confirmed experimentally). The writing-plans handoff accounts for this by detecting subagent availability.

## Test plan

- [x] SDD scaling: 10/10 agents ask permission before eliding reviews on small tasks
- [x] SDD boundary: 9/10 agents delegate to subagents (1 failure on trivial rename edge case)
- [x] SDD check-in: 10/10 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
