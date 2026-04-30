# fix: remove remaining personal project reference from CLAUDE.md

Source: [rtk-ai/rtk#251](https://github.com/rtk-ai/rtk/pull/251)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

- Remove `methode-aristote/app` reference from the JS/TS tooling section (line 379)

Follow-up to #242 (merged). That PR removed 3 personal references; this removes the last one that was missed.

## Changes

`CLAUDE.md` line 379: `Validated on production T3 Stack project (methode-aristote/app)` → `Validated on a production T3 Stack project`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
