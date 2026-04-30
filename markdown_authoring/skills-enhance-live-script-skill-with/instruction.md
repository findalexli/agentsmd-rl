# Enhance Live Script skill with tables support

Source: [matlab/skills#8](https://github.com/matlab/skills/pull/8)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/matlab-live-script/SKILL.md`

## What to add / change

Added section for tables in SKILL.md.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
