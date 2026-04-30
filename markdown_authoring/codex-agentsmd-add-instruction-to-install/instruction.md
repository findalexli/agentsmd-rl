# AGENTS.md: Add instruction to install missing commands

Source: [openai/codex#3807](https://github.com/openai/codex/pull/3807)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This change instructs the model to install any missing command. Else tokens are wasted when it tries to run
commands that aren't available multiple times before installing them.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
