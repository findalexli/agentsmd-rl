# docs: add CLAUDE.md for Claude Code context

Source: [PeonPing/peon-ping#85](https://github.com/PeonPing/peon-ping/pull/85)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Adds CLAUDE.md with project architecture, test commands, and key patterns for future Claude Code sessions
- Covers hook execution flow, CESP event routing, platform audio backends, state management, and testing setup

## Test plan
- [ ] Verify CLAUDE.md content is accurate and concise

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
