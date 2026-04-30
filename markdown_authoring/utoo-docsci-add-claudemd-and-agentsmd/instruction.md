# docs(ci): add CLAUDE.md and AGENTS.md

Source: [utooland/utoo#2602](https://github.com/utooland/utoo/pull/2602)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary
- Add CLAUDE.md with project overview, build/test/lint commands, architecture, and conventions
- Add AGENTS.md with agent workflow guidelines

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
