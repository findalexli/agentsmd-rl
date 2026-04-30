# Add file-tracker skill

Source: [besoeasy/open-skills#2](https://github.com/besoeasy/open-skills/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/chat-logger/SKILL.md`
- `skills/file-tracker/SKILL.md`

## What to add / change

Log all file changes (write, edit, delete) to a SQLite database for debugging and audit trail.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
