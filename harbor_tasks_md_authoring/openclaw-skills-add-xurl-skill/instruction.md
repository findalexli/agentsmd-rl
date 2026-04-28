# skills: add xurl skill

Source: [openclaw/openclaw#21585](https://github.com/openclaw/openclaw/pull/21585)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/xurl/SKILL.md`

## What to add / change

## Summary

- **Problem:** OpenClaw has no built-in skill for interacting with the X (Twitter) API, so agents can't post, search, read, or engage on X without manual setup.
- **Why it matters:** My team at X recently upgraded our `xurl` CLI to support agent-friendly commands, making it a natural fit as an OpenClaw skill. This unlocks X API interactions (posting, replying, searching, DMs, media uploads, etc.) for any OpenClaw agent.
- **What changed:** Added `skills/xurl/SKILL.md` — a new skill reference covering installation, authentication (OAuth 2.0/1.0a/app-only, multi-app support), shortcut commands, raw API access, streaming, and common workflows.
- **What did NOT change (scope boundary):** No core source code, extensions, or existing skills were modified. This is a skill addition only.

## Change Type (select all)

- [ ] Bug fix
- [x] Feature
- [ ] Refactor
- [x] Docs
- [ ] Security hardening
- [ ] Chore/infra

## Scope (select all touched areas)

- [ ] Gateway / orchestration
- [x] Skills / tool execution
- [ ] Auth / tokens
- [ ] Memory / storage
- [x] Integrations
- [ ] API / contracts
- [ ] UI / DX
- [ ] CI/CD / infra

## Linked Issue/PR

- Related: N/A

## User-visible / Behavior Changes

- Agents can now discover and use the `xurl` skill to interact with the X API (post tweets, reply, search, manage followers, send DMs, upload media, etc.) when `xurl` is installed and authenticated.

## Security Impact (required)

- New permiss

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
