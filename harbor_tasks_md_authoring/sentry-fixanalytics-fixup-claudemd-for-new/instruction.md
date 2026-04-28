# fix(analytics): fixup CLAUDE.md for new style of analytics events recording

Source: [getsentry/sentry#98595](https://github.com/getsentry/sentry/pull/98595)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Closes https://linear.app/getsentry/issue/TET-952/update-instructions-for-analytics-instrumentation-in-claudemd

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
