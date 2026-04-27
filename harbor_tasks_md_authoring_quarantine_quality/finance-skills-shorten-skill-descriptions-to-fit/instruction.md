# Shorten skill descriptions to fit 1024-char limit

Source: [himself65/finance-skills#24](https://github.com/himself65/finance-skills/pull/24)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/funda-data/SKILL.md`
- `skills/stock-correlation/SKILL.md`

## What to add / change

## Summary
- Shortens `stock-correlation` description from 1153 to 878 characters
- Shortens `funda-data` description from 1599 to 964 characters
- All 9 skills now fit within the 1024-character limit required by Claude.ai Web

Fixes #21

## Test plan
- [x] Verify all SKILL.md descriptions are under 1024 characters
- [x] Upload stock-correlation zip to Claude.ai Web — should no longer error
- [x] Upload funda-data zip to Claude.ai Web — should also work

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
