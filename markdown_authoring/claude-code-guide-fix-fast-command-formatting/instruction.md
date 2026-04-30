# fix fast command formatting

Source: [OriNachum/claude-code-guide#3](https://github.com/OriNachum/claude-code-guide/pull/3)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/guide/ask/references/built-ins.md`

## What to add / change

Fixes #2

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
