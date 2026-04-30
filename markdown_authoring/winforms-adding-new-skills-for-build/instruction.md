# Adding new skills for Build, Test and downloading correct .NET SDK

Source: [dotnet/winforms#14451](https://github.com/dotnet/winforms/pull/14451)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/building-code/SKILL.md`
- `.github/skills/download-sdk/SKILL.md`
- `.github/skills/running-tests/SKILL.md`

## What to add / change

###### Microsoft Reviewers: [Open in CodeFlow](https://microsoft.github.io/open-pr/?codeflow=https://github.com/dotnet/winforms/pull/14451)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
