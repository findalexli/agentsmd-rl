# misc: use AGENT.md convention

Source: [getlago/lago-front#2677](https://github.com/getlago/lago-front/pull/2677)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Follow [AGENT.md](https://agents.md/) convention.

Also added instructions to use context7 if installed

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
