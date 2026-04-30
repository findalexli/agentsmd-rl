# Added claude skills & some rules

Source: [saleor/saleor#18871](https://github.com/saleor/saleor/pull/18871)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/saleor-django-migration/SKILL.md`
- `saleor/graphql/AGENTS.md`
- `saleor/graphql/CLAUDE.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
