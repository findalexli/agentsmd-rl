# Add eval test authoring skill

Source: [dotnet/skills#409](https://github.com/dotnet/skills/pull/409)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/create-skill-test/SKILL.md`

## What to add / change

### Motivation

Simplify the authoring of the eval scenarios

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
