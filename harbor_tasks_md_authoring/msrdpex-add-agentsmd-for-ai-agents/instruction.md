# Add AGENTS.md for AI agents

Source: [Devolutions/MsRdpEx#165](https://github.com/Devolutions/MsRdpEx/pull/165)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Adds repository-specific guidance for any AI agent (build steps, repo layout, safe-change rules, and packaging notes).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
