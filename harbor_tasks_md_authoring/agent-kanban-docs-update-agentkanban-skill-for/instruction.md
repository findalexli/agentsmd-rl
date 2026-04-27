# docs: update agent-kanban skill for kubectl-style CLI

Source: [saltbo/agent-kanban#60](https://github.com/saltbo/agent-kanban/pull/60)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `skills/agent-kanban/SKILL.md`

## What to add / change

## Summary
- Updated `skills/agent-kanban/SKILL.md` to use new kubectl-style CLI commands (`ak get task`, `ak create note`, etc.) replacing old-style commands (`ak task list`, `ak task log`, etc.)
- Removed references to daemon-managed commands (`assign`, `complete`, `release`, `link`/`unlink`)
- Added task lifecycle subcommands (`claim`, `cancel`, `review`, `reject`) and create task options reference
- Updated `CLAUDE.md` repo linking pattern to use new `ak create repo` / `ak get repo` commands

## Test plan
- [ ] Verify SKILL.md commands match actual CLI implementation
- [ ] Verify CLAUDE.md patterns section is accurate

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
