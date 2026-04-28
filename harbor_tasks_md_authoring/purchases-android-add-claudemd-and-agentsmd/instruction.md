# Add CLAUDE.md and AGENTS.md

Source: [RevenueCat/purchases-android#3082](https://github.com/RevenueCat/purchases-android/pull/3082)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Reverts RevenueCat/purchases-android#2648

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
