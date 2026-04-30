# Simplify proactive-loop SKILL.md

Source: [sonichi/sutando#131](https://github.com/sonichi/sutando/pull/131)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/proactive-loop/SKILL.md`

## What to add / change

## Summary
- Removed dual reactive/proactive loop split
- Single unified 5-min full pass (matches current implementation)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
