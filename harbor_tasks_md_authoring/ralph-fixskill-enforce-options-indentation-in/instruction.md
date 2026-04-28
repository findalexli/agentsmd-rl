# fix(skill): enforce options indentation in prd SKILL.md

Source: [snarktank/ralph#64](https://github.com/snarktank/ralph/pull/64)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/prd/SKILL.md`

## What to add / change

Added reminder to indent options for user responses. Some models (e.g. GLM 4.7) do not indent the options properly. This make hard for the user to read the questions/options.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
