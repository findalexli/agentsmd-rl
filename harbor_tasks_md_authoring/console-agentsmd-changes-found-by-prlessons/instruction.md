# AGENTS.md changes found by pr-lessons skill

Source: [oxidecomputer/console#3081](https://github.com/oxidecomputer/console/pull/3081)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Had Claude go through past PRs and extract lessons from comments that resulted in changes.

https://github.com/david-crespo/dotfiles/blob/4fdad6be5d37d5cf9935e51a3f39baa5657748d3/claude/skills/pr-lessons/SKILL.md

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
