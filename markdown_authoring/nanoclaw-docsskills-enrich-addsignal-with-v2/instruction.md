# docs(skills): enrich /add-signal with v2 lessons learned, drop redundant v2 skill

Source: [qwibitai/nanoclaw#2010](https://github.com/qwibitai/nanoclaw/pull/2010)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-signal/SKILL.md`

## What to add / change

## Summary

- Merges battle-tested lessons from the `/add-signal-v2` skill into the upstream `/add-signal`, then removes the now-redundant v2 skill
- The two skills used different adapter approaches (signal-sdk vs native TCP daemon) but shared most setup knowledge; the valuable parts are architecture-agnostic

## What was added to /add-signal

- **Registration paths**: full new-number (Path A) and linked-device (Path B) flows — previously the upstream assumed an already-linked account
- **CAPTCHA flow**: step-by-step instructions including how to extract the token; this is required for all new registrations
- **VoIP SMS-first timing gotcha**: must request SMS, wait ~60s, then request voice; same captcha token is reusable
- **Java prereq**: signal-cli requires Java 17+; added check + install commands per platform
- **Wiring section**: SQL for DM and group wiring, plus user access grants — without this, new Signal users are silently dropped with `not_member`
- **Config lock warning**: stop the service before running `signal-cli` commands directly; the daemon holds an exclusive lock on its data directory
- **GroupV2 extraction note**: group ID lives at `envelope.dataMessage.groupV2.id`, not `groupInfo.groupId` (GroupV1/legacy) — this is the root cause of the "group replies land in DM" bug

## Factual correction

The upstream stated: *"DMs use your phone number (e.g. `+15555550123`)"* — this is wrong. Signal has used UUID-based identifiers (ACI) since ~0.11.x. DM platform IDs are

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
