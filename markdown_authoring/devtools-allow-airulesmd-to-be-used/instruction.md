# Allow AI_RULES.md to be used by Cursor and Claude

Source: [flutter/devtools#9764](https://github.com/flutter/devtools/pull/9764)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/ai_rules.mdc`
- `CLAUDE.md`

## What to add / change

Follow on to https://github.com/flutter/devtools/issues/9753 to support other popular AI-coding clients

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
