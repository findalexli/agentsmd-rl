# rename Claude.md to CLAUDE.md for cross-platform compatibility

Source: [detekt/detekt#9033](https://github.com/detekt/detekt/pull/9033)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

- Renames `Claude.md` symlink to `CLAUDE.md` for consistent casing across macOS, Windows, and Linux

## Test plan

- [x] Verify symlink still points to AGENTS.md

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
