# feat(develop): Add section to Agent.md for using RFC 2219

Source: [getsentry/sentry-docs#15982](https://github.com/getsentry/sentry-docs/pull/15982)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## DESCRIBE YOUR PR

Add a section to the Agent.md for the the develop docs to use the RFC 2219.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
