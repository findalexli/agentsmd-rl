# Review feedback on dashboard skill

Source: [microsoft/aspire#14642](https://github.com/microsoft/aspire/pull/14642)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/dashboard-testing/SKILL.md`

## What to add / change

Follow up changes for https://github.com/dotnet/aspire/pull/14611

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
