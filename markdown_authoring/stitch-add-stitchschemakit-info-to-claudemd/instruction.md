# Add `StitchSchemaKit` info to Claude.md

Source: [StitchDesign/Stitch#1658](https://github.com/StitchDesign/Stitch/pull/1658)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

For now, using `_V33` examples but there's a note in there about always preferring the latest version.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
