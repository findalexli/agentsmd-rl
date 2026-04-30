# Add CLAUDE.md for Claude Code guidance

Source: [Foundry376/Mailspring-Sync#15](https://github.com/Foundry376/Mailspring-Sync/pull/15)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Provides build commands for Linux/macOS/Windows, runtime configuration,
and documents the architecture including the process model, threading,
key components, and Gmail-specific behavior.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
