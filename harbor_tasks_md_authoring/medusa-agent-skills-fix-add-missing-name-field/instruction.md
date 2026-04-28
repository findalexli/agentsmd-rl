# fix: add missing name field to SKILL.md frontmatter

Source: [medusajs/medusa-agent-skills#1](https://github.com/medusajs/medusa-agent-skills/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/medusa-dev/skills/db-generate/SKILL.md`
- `plugins/medusa-dev/skills/db-migrate/SKILL.md`
- `plugins/medusa-dev/skills/new-user/SKILL.md`

## What to add / change

## Problem

`npx skills add medusajs/medusa-agent-skills --list` (from [vercel-labs/skills](https://github.com/vercel-labs/skills)) only discovers **5 out of 8 skills**.

The 3 missing skills (`db-generate`, `db-migrate`, `new-user`) lack the `name` field in their YAML frontmatter, which is required by the [Agent Skills specification](https://github.com/agentskills/agentskills) for universal skill discovery tools.

## Fix

Added the `name` field to the frontmatter of:
- `plugins/medusa-dev/skills/db-generate/SKILL.md` → `name: db-generate`
- `plugins/medusa-dev/skills/db-migrate/SKILL.md` → `name: db-migrate`
- `plugins/medusa-dev/skills/new-user/SKILL.md` → `name: new-user`

## Before
```
Found 5 skills
```

## After
```
Found 8 skills
```

## Context

The [Agent Skills spec](https://agentskills.io) requires both `name` and `description` fields. Tools like `npx skills` (vercel-labs/skills, 5.7k+ stars) use this to discover skills across 35+ agents (Amp, Claude Code, Cursor, Codex, etc.).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
