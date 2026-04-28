# dev(agents): Move more content into specific AGENTS.md

Source: [getsentry/sentry#105416](https://github.com/getsentry/sentry/pull/105416)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `src/AGENTS.md`
- `static/AGENTS.md`

## What to add / change

The main `AGENTS.md` contained some duplicated information that belongs to the other specific `AGENTS.md`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
