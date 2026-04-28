# claude-api: add Managed Agents memory stores page

Source: [anthropics/skills#1014](https://github.com/anthropics/skills/pull/1014)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/claude-api/SKILL.md`
- `skills/claude-api/shared/managed-agents-api-reference.md`
- `skills/claude-api/shared/managed-agents-core.md`
- `skills/claude-api/shared/managed-agents-environments.md`
- `skills/claude-api/shared/managed-agents-memory.md`
- `skills/claude-api/shared/managed-agents-overview.md`

## What to add / change

## Summary
- Add `shared/managed-agents-memory.md` to the `claude-api` skill covering Managed Agents **Memory Stores** (public beta under `managed-agents-2026-04-01`): object model (`memstore_` / `mem_` / `memver_`), create + seed, attach via `resources[]` (session-create-only, max 8), FUSE mount at `/mnt/memory/<store>/`, host-side CRUD (`create` by path vs `update` by ID), `content_sha256` preconditions, and versions/redact.
- Wire through all cross-references: `SKILL.md` (beta-headers namespace + reading-guide file list), `managed-agents-api-reference.md` (SDK method rows, delete/archive quirks, AddResource note, three new endpoint sections), `managed-agents-core.md` (architecture diagram + `resources[]` enumerations), `managed-agents-environments.md` (Resources intro), `managed-agents-overview.md` (beta-headers table, Reading Guide row, archive bullet).

## Test plan
- [ ] Load the skill and ask "how do I give my managed agent persistent memory" → produces a `resources: [{type: "memory_store", ...}]` example and describes the `/mnt/memory/<store>/` mount
- [ ] Verify all `shared/managed-agents-memory.md` cross-links resolve

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
