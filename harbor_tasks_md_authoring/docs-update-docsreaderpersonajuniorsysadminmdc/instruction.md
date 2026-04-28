# Update docs-reader-persona-junior-sysadmin.mdc

Source: [mattermost/docs#8878](https://github.com/mattermost/docs/pull/8878)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/docs-reader-persona-junior-sysadmin.mdc`

## What to add / change

Update persona

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
