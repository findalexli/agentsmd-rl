# Move compound before sprint summary for clean closure

Source: [garagon/nanostack#80](https://github.com/garagon/nanostack/pull/80)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `ship/SKILL.md`

## What to add / change

## Summary
Reorders the end of /ship so compound runs BEFORE the final sprint summary, not after.

**Before:** ship summary → compound → "Knowledge captured" (abrupt end)
**After:** compound → ship summary with what was built + how to use it + next features (clean closure)

## Context
Found during live test with `--dangerously-skip-permissions`. The full autopilot sprint ran to completion but ended on "Knowledge captured" with no closure. The sprint summary should be the last thing the user sees.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
