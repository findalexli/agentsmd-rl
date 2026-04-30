# Create .cursorrules for CI-aware code reviews

Source: [nntrainer/nntrainer#3650](https://github.com/nntrainer/nntrainer/pull/3650)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursorrules`

## What to add / change

Added cursor rules for code review and CI practices.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
