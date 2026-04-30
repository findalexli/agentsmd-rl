# fix: Fix formatting issue in CLAUDE.md

Source: [archestra-ai/archestra#572](https://github.com/archestra-ai/archestra/pull/572)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Removes trailing period from the introductory sentence in CLAUDE.md for consistency with other documentation headers.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
