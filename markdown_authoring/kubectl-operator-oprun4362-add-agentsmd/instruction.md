# OPRUN-4362: Add AGENTS.md

Source: [operator-framework/kubectl-operator#243](https://github.com/operator-framework/kubectl-operator/pull/243)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Add AGENTS.md to allow agents to make contributions to the codebase.

Assisted by: Claude Code

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
