# [Backport stable/8.8] docs: rename AGENT.md to AGENTS.md

Source: [camunda/camunda#44023](https://github.com/camunda/camunda/pull/44023)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

# Description
Backport of #44019 to `stable/8.8`.

relates to

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
