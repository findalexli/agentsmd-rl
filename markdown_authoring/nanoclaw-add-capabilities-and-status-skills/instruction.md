# add /capabilities and /status skills

Source: [qwibitai/nanoclaw#1086](https://github.com/qwibitai/nanoclaw/pull/1086)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `container/skills/capabilities/SKILL.md`
- `container/skills/status/SKILL.md`

## What to add / change

## Type of Change

- [x] **Skill** - adds a new skill in `.claude/skills/`
- [ ] **Fix** - bug fix or security fix to source code
- [ ] **Simplification** - reduces or simplifies source code

## Description

Adds two read-only container-agent skills for system introspection:

- `/capabilities` — reports installed skills, SDK tools, MCP tools, container utilities, and group info
- `/status` — quick health check: session context, workspace/mount visibility, tool availability, container utilities, and scheduled task snapshot via MCP

Both are main-channel only, enforced by checking for `/workspace/project` mount presence (only mounted for main groups). Non-main groups get a short redirect message.

## For Skills

- [x] I have not made any changes to source code
- [x] My skill contains instructions for Claude to follow (not pre-built code)
- [x] I tested this skill on a fresh clone

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
