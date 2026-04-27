# docs(skill): improve SKILL.md triggers and structure

Source: [avivsinai/agent-message-queue#4](https://github.com/avivsinai/agent-message-queue/pull/4)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/amq-cli/SKILL.md`
- `.codex/skills/amq-cli/SKILL.md`
- `skills/amq-cli/SKILL.md`

## What to add / change

## Summary

- Add explicit trigger keywords to skill description for better discoverability
- Move inject modes section under Wake Notifications where it belongs
- Replace external GitHub link with internal references section
- Add "when to read" guidance for reference files

## Changes

All three skill copies updated (via `make sync-skills`):
- `.claude/skills/amq-cli/SKILL.md`
- `.codex/skills/amq-cli/SKILL.md`
- `skills/amq-cli/SKILL.md`

## Test plan

- [x] Verified skill files are identical across all locations
- [x] Pre-push checks passed (vet, lint, test, smoke)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
