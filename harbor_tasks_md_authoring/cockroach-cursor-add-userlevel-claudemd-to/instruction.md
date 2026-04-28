# cursor: add user-level CLAUDE.md to rule

Source: [cockroachdb/cockroach#153066](https://github.com/cockroachdb/cockroach/pull/153066)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/main.mdc`

## What to add / change

Useful for user-level preferences like gh to access Github, etc.

Epic: none
Release note: None

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
