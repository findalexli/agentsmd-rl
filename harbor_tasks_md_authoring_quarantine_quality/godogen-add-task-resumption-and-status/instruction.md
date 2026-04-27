# Add task resumption and status tracking to gamedev agent

Source: [htdt/godogen#6](https://github.com/htdt/godogen/pull/6)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/game-decomposer.md`
- `.claude/agents/gamedev.md`
- `.claude/agents/godot-task.md`

## What to add / change

## Summary
Enhanced the gamedev agent pipeline to support resuming interrupted work and tracking task progress through explicit status fields in PLAN.md. This makes the pipeline idempotent and allows multi-session projects to pick up where they left off without losing context.

## Key Changes

**gamedev.md:**
- Added resume check at pipeline start: if `build/PLAN.md` exists, skip scaffold/decomposer and jump to task execution
- Introduced `**Status:**` field tracking for each task (pending, in_progress, done, done (partial), skipped)
- Updated task execution loop to mark status before launching sub-agent and after reading results
- Added "Resuming an Interrupted Pipeline" section documenting how to find and retry incomplete tasks
- Clarified that PLAN.md status fields are owned by the gamedev agent, not the decomposer

**game-decomposer.md:**
- Refined Requirements guidance: focus on high-level player experience rather than implementation details or pixel-exact specs
- Reduced emphasis on merge tasks: added note that most simple projects don't need them, only add when integration is genuinely non-trivial
- Updated merge task guidance to integrate 2-3 things at a time, not everything at once
- Clarified that Requirements should specify *what* players experience, not *how* to implement
- Added "What NOT to Include" section warning against detailed technical specs and unnecessary merge tasks

**godot-task.md:**
- Enhanced visual verification step to check both task goal match an

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
