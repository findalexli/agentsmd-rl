# Add skill for dashboard testing

Source: [microsoft/aspire#14611](https://github.com/microsoft/aspire/pull/14611)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/dashboard-testing/SKILL.md`
- `AGENTS.md`

## What to add / change

Add skill for dashboard testing. Explain difference between test projects, when to use each, how to write good bunit component tests.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
