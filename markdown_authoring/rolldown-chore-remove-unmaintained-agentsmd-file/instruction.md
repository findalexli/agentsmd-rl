# chore: remove unmaintained AGENTS.md file

Source: [rolldown/rolldown#6009](https://github.com/rolldown/rolldown/pull/6009)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Removing AGENTS.md as it contains outdated information and one one maintains it.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
