# chore: replace CLAUDE.md with AGENTS.md

Source: [codebar/planner#2485](https://github.com/codebar/planner/pull/2485)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This allows more coding agents (hello OpenCode) to understand how to work well inside this repository.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
