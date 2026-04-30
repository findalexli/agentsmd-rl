# fix(whatsapp): use sender's JID for DM-with-bot registration, skip trigger

Source: [qwibitai/nanoclaw#751](https://github.com/qwibitai/nanoclaw/pull/751)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-whatsapp/SKILL.md`

## What to add / change

Closes #750

## Type of Change

- [ ] **Skill** - adds a new skill in `.claude/skills/`
- [x] **Fix** - bug fix or security fix to source code
- [ ] **Simplification** - reduces or simplifies source code

## Description

Two bugs in the "dedicated number + DM with bot" setup path:

1. **Wrong JID** — the skill used the bot's own number as the registration JID. Incoming DMs arrive with the *sender's* JID (the user's personal number), so no messages ever matched → bot silently ignored all messages. Fix: ask for the user's personal number and register that.

2. **Trigger required** — `--no-trigger-required` was only applied for self-chat, not DM with bot. A trigger prefix in a private 1:1 DM is unnecessary. Fix: apply `--no-trigger-required` for both self-chat and DM with bot.

## For Skills

- [x] I have not made any changes to source code
- [x] My skill contains instructions for Claude to follow (not pre-built code)
- [ ] I tested this skill on a fresh clone

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
