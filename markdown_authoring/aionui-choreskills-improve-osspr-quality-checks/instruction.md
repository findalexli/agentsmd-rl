# chore(skills): improve oss-pr quality checks documentation

Source: [iOfficeAI/AionUi#2185](https://github.com/iOfficeAI/AionUi/pull/2185)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/oss-pr/SKILL.md`

## What to add / change

## Summary

- Restructure Step 1 quality checks as a table with clear scope and skip conditions for each command
- Change execution order to `format` → `lint` → `tsc`, ensuring format always runs even for non-code files
- Update quick reference section to match the new order and skip logic

## Test plan

- [ ] Verify oss-pr skill correctly skips lint/tsc when no `.ts/.tsx` files are changed
- [ ] Verify format always runs regardless of file types

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
