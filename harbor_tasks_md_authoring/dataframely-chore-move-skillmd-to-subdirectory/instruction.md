# chore: Move `SKILL.md` to subdirectory

Source: [Quantco/dataframely#312](https://github.com/Quantco/dataframely/pull/312)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/SKILL.md`

## What to add / change

# Motivation

The current design causes the entire repo to be cloned to `.agent/skills` when using `npx skills add Quantco/dataframely`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
