# Enforce PR file-list confirmation rule in AGENTS

Source: [FrankChen021/datastoria#101](https://github.com/FrankChen021/datastoria/pull/101)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- strengthen AGENTS commit rules for PR workflow
- require listing changed files vs master for each branch before PR creation
- require explicit user approval before running gh pr create

## Testing
- documentation-only change

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
