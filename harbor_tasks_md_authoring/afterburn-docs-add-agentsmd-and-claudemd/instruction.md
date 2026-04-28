# docs: Add AGENTS.md and CLAUDE.md for AI coding assistants

Source: [coreos/afterburn#1271](https://github.com/coreos/afterburn/pull/1271)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

AGENTS.md provides a concise repository specification for tool-agnostic AI coding assistants (OpenCode, Cursor, etc). CLAUDE.md imports AGENTS.md due to claude not looking for AGENTS.md automatically.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
