# Fix test commands in AGENTS.md

Source: [withastro/astro#15500](https://github.com/withastro/astro/pull/15500)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Changes

- Test commands were wrong, those commands don't even work.
- Clarifies how to run with `pnpm` and the different ways to run individual tests.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
