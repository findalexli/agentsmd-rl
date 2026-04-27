# chore: rework PR title and description guidance

Source: [langchain-ai/langchain#36917](https://github.com/langchain-ai/langchain/pull/36917)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Rework the PR and commit guidance in the agent guidelines so new contributors (human and AI) produce descriptions and titles that age well.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
