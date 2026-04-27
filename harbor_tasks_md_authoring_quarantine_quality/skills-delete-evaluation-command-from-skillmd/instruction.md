# Delete Evaluation Command from SKILL.md

Source: [matlab/skills#2](https://github.com/matlab/skills/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/matlab-live-script/SKILL.md`

## What to add / change

Removed the Evaluation Command section from SKILL.md. Fixes Issue #1

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
