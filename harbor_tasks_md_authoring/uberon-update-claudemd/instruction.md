# Update CLAUDE.md

Source: [obophenotype/uberon#3547](https://github.com/obophenotype/uberon/pull/3547)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Added instruction to reserialise with ROBOT before committing.
FIxes #3545

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
