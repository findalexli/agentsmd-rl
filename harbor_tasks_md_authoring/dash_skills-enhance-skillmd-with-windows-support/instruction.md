# Enhance SKILL.md with Windows support guidelines

Source: [kevmoo/dash_skills#10](https://github.com/kevmoo/dash_skills/pull/10)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agent/skills/dart-cli-app-best-practices/SKILL.md`

## What to add / change

Added section on Windows compatibility for CLI apps.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
