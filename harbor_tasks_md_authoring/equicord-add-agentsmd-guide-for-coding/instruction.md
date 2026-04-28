# Add AGENTS.md guide for coding agents

Source: [Equicord/Equicord#815](https://github.com/Equicord/Equicord/pull/815)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Adds a comprehensive AGENTS.md guide for AI coding agents working on Equicord, based on the [agents.md](https://agents.md/) standard format.
**Also adds:**
- CLAUDE.md symlink for Claude Code compatibility

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
