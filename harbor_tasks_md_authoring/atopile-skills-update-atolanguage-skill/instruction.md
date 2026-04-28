# Skills: Update ato-language skill

Source: [atopile/atopile#1679](https://github.com/atopile/atopile/pull/1679)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/ato-language/EXTENSION.md`
- `.claude/skills/ato-language/SKILL.md`

## What to add / change

Based off Opus 4.6 analysis of all package examples and atopile source/compiler analysis.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
