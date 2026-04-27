# Fix description length for earnings-recap and estimate-analysis

Source: [himself65/finance-skills#27](https://github.com/himself65/finance-skills/pull/27)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/earnings-recap/SKILL.md`
- `skills/estimate-analysis/SKILL.md`

## What to add / change

## Summary
- Shortens `earnings-recap` description from 1032 to 876 characters
- Shortens `estimate-analysis` description from 1209 to 920 characters
- Fixes the skill-lint CI failure on main

## Test plan
- [x] Verify skill-lint CI passes on this PR

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
