# add AGENTS.md

Source: [JetBrains/youtrackdb#684](https://github.com/JetBrains/youtrackdb/pull/684)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

#### Motivation:

Codex (and other agents) is expected to auto-discover AGENTS.md on session start. Adding a minimal AGENTS.md that points to CLAUDE.md ensures repo-specific guidance is reliably loaded without manual prompts, keeping agent behavior consistent with project conventions and reducing onboarding friction.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
