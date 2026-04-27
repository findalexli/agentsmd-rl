# fix: correct AM_ROOT guidance in skill docs

Source: [avivsinai/agent-message-queue#33](https://github.com/avivsinai/agent-message-queue/pull/33)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/amq-cli/SKILL.md`
- `.codex/skills/amq-cli/SKILL.md`
- `skills/amq-cli/SKILL.md`

## What to add / change

## Summary

- Fix misleading `AM_ROOT` example in SKILL.md that caused agents to append `/collab` when outside `coop exec`, routing messages to the wrong mailbox
- Replace with correct `eval "$(amq env --me claude)"` pattern
- Add root resolution truth-table covering all 4 contexts (outside/inside coop exec, with/without session)
- Synced across all 3 skill copies (.claude/, .codex/, skills/)

Bug found during live PR review session — both Claude and Codex independently hit the same misrouting issue.

## Test plan

- [x] `make ci` passes (pre-push hook)
- [x] All 3 skill copies verified identical
- [x] Smoke test passes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
