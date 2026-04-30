# updates to claude.md file

Source: [allenai/OLMo-core#612](https://github.com/allenai/OLMo-core/pull/612)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Followup to #611.

- Adds a section about docstrings
- More info about tests
- Mentioned examples folder

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
