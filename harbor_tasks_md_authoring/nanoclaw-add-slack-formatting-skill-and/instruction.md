# Add Slack formatting skill and update message formatting guides

Source: [qwibitai/nanoclaw#1300](https://github.com/qwibitai/nanoclaw/pull/1300)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `container/skills/slack-formatting/SKILL.md`
- `groups/global/CLAUDE.md`
- `groups/main/CLAUDE.md`

## What to add / change

## Type of Change

- [x] **Skill** - adds a new skill in `container/skills/`
- [ ] **Fix** - bug fix or security fix to source code
- [ ] **Simplification** - reduces or simplifies source code

## Description

This PR adds comprehensive Slack message formatting guidance to help Claude format messages correctly when responding to Slack channels.

### Changes

1. **New Skill: `slack-formatting`** (`container/skills/slack-formatting/SKILL.md`)
   - Complete reference for Slack mrkdwn syntax
   - Detection rules for Slack context (folder prefix `slack_`)
   - Formatting reference for text styles, links, mentions, lists, quotes, and emoji
   - Clear "What NOT to use" section highlighting common mistakes
   - Example message and quick rules for easy reference

2. **Updated `groups/main/CLAUDE.md`**
   - Expanded "Message Formatting" section to cover multiple platforms
   - Added Slack-specific formatting rules with reference to the new skill
   - Clarified WhatsApp/Telegram formatting rules
   - Added Discord formatting guidance (standard Markdown)

3. **Updated `groups/global/CLAUDE.md`**
   - Replaced generic WhatsApp-only formatting guidance with platform-aware instructions
   - Added Slack, WhatsApp/Telegram, and Discord formatting sections
   - Consistent with main group guidance

### Rationale

Slack uses mrkdwn syntax which differs significantly from standard Markdown. Without clear guidance, Claude may format messages incorrectly (e.g., using `**bold**` instead of `*bold*`,

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
