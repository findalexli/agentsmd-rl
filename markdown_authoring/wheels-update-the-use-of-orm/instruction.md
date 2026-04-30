# Update the use of ORM functions in claude.md files

Source: [wheels-dev/wheels#1736](https://github.com/wheels-dev/wheels/pull/1736)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `templates/base/src/app/CLAUDE.md`
- `templates/base/src/app/controllers/CLAUDE.md`
- `templates/base/src/app/jobs/CLAUDE.md`
- `templates/base/src/app/lib/CLAUDE.md`
- `templates/base/src/app/mailers/CLAUDE.md`
- `templates/base/src/app/models/CLAUDE.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
