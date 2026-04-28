# Add AGENTS.md symlink to CLAUDE.md

Source: [a16z/jolt#1263](https://github.com/a16z/jolt/pull/1263)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Adds `AGENTS.md` as a symlink to `CLAUDE.md` so AI coding agents that look for `AGENTS.md` pick up the same project instructions.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
