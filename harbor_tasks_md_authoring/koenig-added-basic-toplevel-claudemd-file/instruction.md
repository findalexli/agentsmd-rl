# Added basic top-level CLAUDE.md file

Source: [TryGhost/Koenig#1607](https://github.com/TryGhost/Koenig/pull/1607)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

no issue

- `/init` output with minor modifications for correctness

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
