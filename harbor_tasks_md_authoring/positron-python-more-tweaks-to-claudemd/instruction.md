# python: more tweaks to CLAUDE.md

Source: [posit-dev/positron#11976](https://github.com/posit-dev/positron/pull/11976)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `extensions/positron-python/CLAUDE.md`

## What to add / change

Let's cut down on a few redundant tokens.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
