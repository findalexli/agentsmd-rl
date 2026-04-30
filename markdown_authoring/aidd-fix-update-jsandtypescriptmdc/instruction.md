# fix: update js-and-typescript.mdc

Source: [paralleldrive/aidd#7](https://github.com/paralleldrive/aidd/pull/7)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `ai/js-and-typescript.mdc`

## What to add / change

Fix bug in rules.

Cursor would mistakenly include the quotes and read the rule as `"**.*js` which doesn't target any files and similarly `**/*.tsx"` which doesn't target any files, neither.

Also, `alwaysApply: true` ignores the glob pattern and includes the context for any file, which depletes attention capacity unnecessarily for unrelated files.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
