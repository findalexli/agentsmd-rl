# Add proper front-matter to SKILL.md for claude-api

Source: [anthropics/skills#897](https://github.com/anthropics/skills/pull/897)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/claude-api/SKILL.md`

## What to add / change

otherwise it's not a proper skill, and can't be installed or read properly by agents

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
