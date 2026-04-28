# feat: add AGENTS.md

Source: [alpic-ai/skybridge#424](https://github.com/alpic-ai/skybridge/pull/424)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

With instructions for Greptile to verify core and skills/docs are in sync. Tested, seems to work OK.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
