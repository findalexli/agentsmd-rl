# Add SKILL.md for infographic creation guidelines

Source: [antvis/Infographic#91](https://github.com/antvis/Infographic/pull/91)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

Usage: https://code.claude.com/docs/en/skills#personal-skills

- https://github.com/antvis/Infographic/issues/76

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
