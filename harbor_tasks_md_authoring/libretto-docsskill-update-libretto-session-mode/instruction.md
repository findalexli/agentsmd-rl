# docs(skill): update libretto session mode guidance

Source: [saffron-health/libretto#31](https://github.com/saffron-health/libretto/pull/31)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/libretto/SKILL.md`

## What to add / change

## Summary
- add explicit required session-mode announcements for read-only and full-access workflows
- replace `interactive` terminology with `full-access` in commands and examples
- update browser-agent debugging steps to require explicit full-access approval before exec/run actions

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
