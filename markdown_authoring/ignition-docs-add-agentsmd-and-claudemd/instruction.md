# docs: add AGENTS.md and CLAUDE.md for AI coding assistants

Source: [coreos/ignition#2223](https://github.com/coreos/ignition/pull/2223)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

AGENTS.md provides a concise repository specification for tool-agnostic AI coding assistants (OpenCode, Cursor, etc). CLAUDE.md imports AGENTS.md since claude does not auto load AGENTS.md

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
