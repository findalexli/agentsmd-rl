# chore: fix deprecated --testPathPattern in CLAUDE.md

Source: [concord-consortium/codap#2420](https://github.com/concord-consortium/codap/pull/2420)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Updates the test pattern matching example to pass the pattern directly instead of using `--testPathPattern`, which is deprecated in recent Jest versions

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
