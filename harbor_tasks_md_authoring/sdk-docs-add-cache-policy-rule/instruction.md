# docs: add cache policy rule for AI assistants

Source: [vargHQ/sdk#110](https://github.com/vargHQ/sdk/pull/110)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Adds a **Cache Policy** section to CLAUDE.md instructing AI assistants to never clear or delete user cache during debugging.

## Changes

- Added cache policy rules to CLAUDE.md:
  - Never delete cached generations (they cost $0.05–$0.50+ each)
  - Suggest alternatives: `--no-cache` flag, modified prompts, or asking the user
  - Treat cache as production data, not disposable debug state

Closes #46

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
