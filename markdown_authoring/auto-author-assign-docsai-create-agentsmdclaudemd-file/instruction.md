# docs(ai): Create `AGENTS.md`(`CLAUDE.md`) file

Source: [toshimaru/auto-author-assign#125](https://github.com/toshimaru/auto-author-assign/pull/125)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Add project documentation for Claude Code including:
- Project overview and tech stack
- Common build commands
- Project structure
- Key development notes about rebuilding dist
- Action behavior and configuration

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
