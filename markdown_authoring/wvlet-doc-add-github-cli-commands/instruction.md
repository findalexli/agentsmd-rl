# doc: Add GitHub CLI commands section to CLAUDE.md

Source: [wvlet/wvlet#1169](https://github.com/wvlet/wvlet/pull/1169)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Added GitHub CLI commands section with common PR management commands
- Provides quick reference for reading PR review comments, checking status, and merging

## Test plan
- [x] Verify CLAUDE.md formatting is correct
- [x] Confirm all GitHub CLI commands are valid

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
