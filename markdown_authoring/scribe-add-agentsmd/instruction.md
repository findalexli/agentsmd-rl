# Add AGENTS.md

Source: [knuckleswtf/scribe#1055](https://github.com/knuckleswtf/scribe/pull/1055)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Adds an AGENTS.md file to help guide AI coding agents with project-specific context, commands, and conventions.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
