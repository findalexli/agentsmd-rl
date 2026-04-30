# docs: add worktree instruction to AGENTS.md

Source: [Kilo-Org/kilo#508](https://github.com/Kilo-Org/kilo/pull/508)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Adds a one-liner to AGENTS.md instructing agents that they may be running in a git worktree and must make all changes in their current working directory, never in the main repo checkout.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
