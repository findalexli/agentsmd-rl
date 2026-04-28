# chore(cc): claude.md pruning for shadcn

Source: [remeda/remeda#1327](https://github.com/remeda/remeda/pull/1327)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/docs/CLAUDE.md`

## What to add / change

Following #1324

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
