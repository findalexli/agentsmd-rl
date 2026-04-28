# Add `AGENTS.md` for AI coding agents

Source: [diffblue/hw-cbmc#1658](https://github.com/diffblue/hw-cbmc/pull/1658)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Documents the build system, testing infrastructure, coding conventions, architectural concepts, and git conventions to help AI coding agents (Claude Code, Kiro, Copilot, etc.) work effectively with this codebase.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
