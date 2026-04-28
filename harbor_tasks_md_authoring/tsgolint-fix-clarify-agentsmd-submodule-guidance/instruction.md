# fix: clarify `AGENTS.md` submodule guidance

Source: [oxc-project/tsgolint#909](https://github.com/oxc-project/tsgolint/pull/909)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Clarifies AGENTS.md guidance for typescript-go submodule commits and resets.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
