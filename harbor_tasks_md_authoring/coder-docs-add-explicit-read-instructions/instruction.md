# docs: add explicit read instructions for non-Claude-Code agents

Source: [coder/coder#23403](https://github.com/coder/coder/pull/23403)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

The @ imports at the bottom of this file are auto-loaded by Claude Code
but silently ignored by other agent runtimes (Coder Agents, Zed, etc.).
Add an explicit fallback so those agents know what to read and when.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
