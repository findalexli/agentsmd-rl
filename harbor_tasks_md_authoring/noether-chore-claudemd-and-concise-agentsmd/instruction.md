# chore: CLAUDE.md and concise AGENTS.md

Source: [Emmi-AI/noether#163](https://github.com/Emmi-AI/noether/pull/163)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Claude Code doesn't support AGENTS.md: https://github.com/anthropics/claude-code/issues/6235, the easy fix is to just reference it from a CLAUDE.md

At this chance I also shortened the AGENTS.md for things that I think are not important, happy to discuss.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
