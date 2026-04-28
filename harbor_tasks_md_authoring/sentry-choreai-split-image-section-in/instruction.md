# chore(AI): Split image section in AGENTS.md file

Source: [getsentry/sentry#101271](https://github.com/getsentry/sentry/pull/101271)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `static/AGENTS.md`

## What to add / change

Splits out an Image section in AGENTS.md. Also adds Avatar guidance from https://sentry.sentry.io/stories/core/avatar

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
