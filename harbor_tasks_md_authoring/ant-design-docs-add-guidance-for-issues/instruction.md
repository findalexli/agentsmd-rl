# docs: add guidance for issues fixed but not yet released

Source: [ant-design/ant-design#57121](https://github.com/ant-design/ant-design/pull/57121)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/issue-reply/SKILL.md`

## What to add / change

## Summary

- Add guidance for handling cases where PR is merged but new version is not yet published
- Add reply templates in both English and Chinese for this scenario

## Context

When closing duplicate issues that have been fixed but the fix hasn't been released yet, we need to inform users to wait for the new version instead of saying it's already fixed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
