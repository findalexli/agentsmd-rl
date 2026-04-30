# bugbot: add disclosure to agents.md

Source: [getsentry/sentry#102172](https://github.com/getsentry/sentry/pull/102172)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `static/AGENTS.md`

## What to add / change

Add Disclosure guidelines to AGENTS.md so that it can hopefully catch [instances](https://github.com/getsentry/sentry/pull/102144) where we reimplement this patterns

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
