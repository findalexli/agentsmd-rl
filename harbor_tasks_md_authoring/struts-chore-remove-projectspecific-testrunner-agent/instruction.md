# chore: remove project-specific test-runner agent

Source: [apache/struts#1613](https://github.com/apache/struts/pull/1613)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/test-runner.md`

## What to add / change

## Summary
- Removed project-specific test-runner agent from `.claude/agents/`
- The agent has been moved to user-wide `~/.claude/agents/` where it is now project-agnostic and auto-detects build tools (Maven, Gradle, sbt, npm, Python, Go, Cargo)

## Test plan
- [x] Verify agent file is deleted from project
- [x] Verify user-wide agent works across projects

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
