# chore: init agents.md

Source: [kubeshop/testkube#6876](https://github.com/kubeshop/testkube/pull/6876)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Added the most valuable information to the root agents.md , we can add more info in package-sepecific agents.md files.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
