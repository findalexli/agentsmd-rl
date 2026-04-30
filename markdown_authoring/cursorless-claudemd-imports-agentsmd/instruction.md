# CLAUDE.md imports AGENTS.md

Source: [cursorless-dev/cursorless#3165](https://github.com/cursorless-dev/cursorless/pull/3165)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

@pokey Mind testing this?

edit: The solution for working with Claude or other agents that doesn't natively support AGENTS.md is to create a symbolic link.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
