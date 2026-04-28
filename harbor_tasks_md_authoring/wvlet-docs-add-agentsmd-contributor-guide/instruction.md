# docs: add AGENTS.md contributor guide

Source: [wvlet/wvlet#1142](https://github.com/wvlet/wvlet/pull/1142)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Adds AGENTS.md titled "Repository Guidelines" with project structure, build/test commands, coding style, testing, PR rules, and debug logging notes. Tailored to this repo’s SBT multi-project + UI workspaces.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
