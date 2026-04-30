# [6.x] Adds AGENTS.md and testing guidelines skill

Source: [craftcms/cms#18388](https://github.com/craftcms/cms/pull/18388)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/testing-guidelines/SKILL.md`
- `.agents/skills/testing-guidelines/references/testing-guidelines.md`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
