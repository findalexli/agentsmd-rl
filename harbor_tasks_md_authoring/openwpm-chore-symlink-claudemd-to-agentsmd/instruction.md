# chore: symlink CLAUDE.md to AGENTS.md

Source: [openwpm/OpenWPM#1135](https://github.com/openwpm/OpenWPM/pull/1135)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Adds a `CLAUDE.md` symlink pointing to `AGENTS.md` so Claude Code automatically picks up project instructions

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
