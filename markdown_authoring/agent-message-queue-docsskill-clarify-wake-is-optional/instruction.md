# docs(skill): clarify --wake is optional and requires interactive terminal

Source: [avivsinai/agent-message-queue#13](https://github.com/avivsinai/agent-message-queue/pull/13)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/amq-cli/SKILL.md`
- `.codex/skills/amq-cli/SKILL.md`
- `skills/amq-cli/SKILL.md`

## What to add / change

## Summary
- Remove `--wake` from Quick Reference setup examples (not required for send/receive)
- Add explicit callout that AI agents should skip wake section (no TTY access)
- Clarify wake is for human operators in interactive terminals only
- Move `--wake` to end of `amq env` examples with clarifying comment

## Problem
The Quick Reference showed:
```bash
eval "$(amq env --me claude --wake)"
```

This led AI agents to think `--wake` was required for messaging. In reality:
- `--wake` is **only for receiving** notifications (not sending)
- `--wake` requires an interactive terminal with TTY/TIOCSTI access
- AI agents running non-interactively cannot use wake at all

## Changes
Following 2026 skill authoring best practices from [Anthropic's docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):
- Keep instructions concise and specific
- Be explicit about requirements and constraints
- Separate optional features from required setup

## Test plan
- [ ] Verify skill installs correctly
- [ ] Verify `amq send` works without `--wake`
- [ ] Verify documentation renders correctly

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
