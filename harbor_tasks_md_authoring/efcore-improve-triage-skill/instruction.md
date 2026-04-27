# Improve triage skill

Source: [dotnet/efcore#37955](https://github.com/dotnet/efcore/pull/37955)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/triage/SKILL.md`

## What to add / change

Add labeling, type classification...

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
