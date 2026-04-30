# AI: add missing AGENTS.md files

Source: [rsyslog/rsyslog#6187](https://github.com/rsyslog/rsyslog/pull/6187)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `runtime/AGENTS.md`
- `tests/AGENTS.md`

## What to add / change

The last commit which I made were missing these files. Now adding them.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
