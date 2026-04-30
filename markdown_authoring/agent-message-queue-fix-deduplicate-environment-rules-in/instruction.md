# fix: deduplicate Environment Rules in SKILL.md

Source: [avivsinai/agent-message-queue#32](https://github.com/avivsinai/agent-message-queue/pull/32)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/amq-cli/SKILL.md`
- `.codex/skills/amq-cli/SKILL.md`
- `skills/amq-cli/SKILL.md`

## What to add / change

## Summary
- Remove duplicated "Environment Rules (IMPORTANT)" section in SKILL.md
- The section appeared twice with overlapping content after PR #28 merge
- Synced to all 3 skill locations via `make sync-skills`

## Test plan
- [x] `make ci` passes
- [x] `make sync-skills` propagated to all 3 locations

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
