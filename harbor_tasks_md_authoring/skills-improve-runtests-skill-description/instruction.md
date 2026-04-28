# Improve run-tests skill description

Source: [dotnet/skills#372](https://github.com/dotnet/skills/pull/372)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/dotnet-test/skills/run-tests/SKILL.md`

## What to add / change

Improves the description using the prompt from Manish

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
