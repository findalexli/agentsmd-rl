# Redirect Claude Code to read AGENTS.md

Source: [microsoft/TypeScript#63446](https://github.com/microsoft/TypeScript/pull/63446)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Per https://github.com/microsoft/TypeScript/pull/63439#issuecomment-4328732077, it seems like Claude Code isn't reading AGENTS.md.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
