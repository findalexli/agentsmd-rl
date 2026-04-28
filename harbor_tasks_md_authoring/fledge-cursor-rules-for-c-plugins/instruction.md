# Cursor Rules for C++ Plugins

Source: [fledge-iot/fledge#1673](https://github.com/fledge-iot/fledge/pull/1673)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/C/core.mdc`
- `.cursor/rules/C/plugins/filter.mdc`
- `.cursor/rules/C/plugins/north.mdc`
- `.cursor/rules/C/plugins/south.mdc`
- `.cursor/rules/README.md`
- `.cursor/services/notification.mdc`
- `.cursor/services/notification_code_review.mdc`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
