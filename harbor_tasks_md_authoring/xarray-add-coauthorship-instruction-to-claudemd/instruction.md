# Add co-authorship instruction to CLAUDE.md

Source: [pydata/xarray#10748](https://github.com/pydata/xarray/pull/10748)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Added instruction to include co-authorship trailer in commits

This ensures proper attribution when Claude assists with code contributions.

[This is Claude Code on behalf of the user]

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
