# feat: add agentmail skill

Source: [sickn33/antigravity-awesome-skills#183](https://github.com/sickn33/antigravity-awesome-skills/pull/183)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/agentmail/SKILL.md`

## What to add / change

## Summary

Adds an AgentMail skill — email infrastructure for AI agents.

**What it does:** Gives agents the ability to create email accounts, send/receive emails, manage webhooks, and handle email-based workflows via the AgentMail API.

**Use case:** AI agents that need email capabilities — signing up for services, receiving verification emails, communicating with users, or monitoring inboxes. No domain setup required. Karma-based rate limiting instead of traditional spam filters.

- Skill file: `skills/agentmail/SKILL.md`
- Includes full API reference, SDK examples, webhook signature verification, and common patterns

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
