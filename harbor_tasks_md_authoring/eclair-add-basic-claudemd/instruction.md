# Add basic CLAUDE.md

Source: [ACINQ/eclair#3254](https://github.com/ACINQ/eclair/pull/3254)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

This was generated using Opus 4.6 with the `/init` command. It provides overall context about the codebase to every Claude session, to avoid repeating work to build that context (consume less token whenever using Claude for a task).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
