# Release: Fix marketing-ideas numbering

Source: [coreyhaines31/marketingskills#19](https://github.com/coreyhaines31/marketingskills/pull/19)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/marketing-ideas/SKILL.md`

## What to add / change

Merges development into main with sequential numbering fix for marketing-ideas skill.

See PR #18 for details.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
