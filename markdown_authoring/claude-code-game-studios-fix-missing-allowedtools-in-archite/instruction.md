# Fix missing allowed-tools in /architecture-decision and /story-done

Source: [Donchitos/Claude-Code-Game-Studios#36](https://github.com/Donchitos/Claude-Code-Game-Studios/pull/36)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/architecture-decision/SKILL.md`
- `.claude/skills/story-done/SKILL.md`

## What to add / change

## Summary

- Adds `Edit` to `/architecture-decision` `allowed-tools` — retrofit mode and registry append both call `Edit` on existing files, causing a permission error on every `/architecture-decision retrofit` run
- Adds `Write` to `/story-done` `allowed-tools` — Phase 7 creates `active.md` on first run; missing `Write` caused silent failure and lost completion notes

Closes #33. Bug found and fix branches prepared by @xiaolai via [NLPM](https://github.com/xiaolai/nlpm-for-claude) audit. Great catch.

## Test plan

- [ ] Run `/architecture-decision retrofit <existing-adr>` — should complete without permission error
- [ ] Run `/story-done` on a fresh project (no `active.md`) — should create `active.md` successfully

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
