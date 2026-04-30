# build: update rules for chrome-release-cls skill

Source: [electron/electron#51140](https://github.com/electron/electron/pull/51140)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/chrome-release-cls/SKILL.md`

## What to add / change

#### Description of Change

Followup to https://github.com/electron/electron/pull/51138

#### Release Notes

Notes: none

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
