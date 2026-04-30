# Update `.cursorrules` and `claude.md` for Stagehand V3

Source: [browserbase/stagehand#1183](https://github.com/browserbase/stagehand/pull/1183)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursorrules`
- `claude.md`

## What to add / change

# why
Coding agents should have updated context for the new syntax and features of Stagehand V3.

# what changed
Updated `.cursorrules` and `claude.md`

# test plan

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
