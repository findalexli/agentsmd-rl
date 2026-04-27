# Ensure create-skill mentions codeowners

Source: [dotnet/skills#478](https://github.com/dotnet/skills/pull/478)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/create-skill/SKILL.md`

## What to add / change

I have seen many times Copilot not modifying the codeowners file when creating a new skill. With this change, we are now correctly updating it.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
