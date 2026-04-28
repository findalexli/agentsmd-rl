# docs: add AGENTS.md and CLAUDE.md for AI agents

Source: [coreos/butane#697](https://github.com/coreos/butane/pull/697)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

When you use AI coding tools (Claude Code, OpenCode, Cursor, etc.) in this repo, they now automatically load context about how we do things here - commit formats, testing requirements, architecture, etc.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
