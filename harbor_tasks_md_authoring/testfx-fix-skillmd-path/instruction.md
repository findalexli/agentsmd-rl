# Fix SKILL.md path

Source: [microsoft/testfx#7655](https://github.com/microsoft/testfx/pull/7655)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/post-release-activities/SKILL.md`

## What to add / change

<!-- 
- Add a brief summary of what this Pull Request is about.
- Add a link to the issue this Pull Request relates to.
-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
