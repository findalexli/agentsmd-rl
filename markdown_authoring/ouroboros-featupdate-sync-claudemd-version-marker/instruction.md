# feat(update): sync CLAUDE.md version marker after upgrade

Source: [Q00/ouroboros#139](https://github.com/Q00/ouroboros/pull/139)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/update/SKILL.md`

## What to add / change

## Summary

- After `ooo update` upgrades the PyPI package and plugin, it now checks if the current project's `CLAUDE.md` has an Ouroboros block (`<!-- ooo:VERSION:X.Y.Z -->`) with a stale version marker
- If found, it updates the marker to match the newly installed version
- Adds guidance in post-update output to run `ooo setup` if block content changed between versions

## Problem

When a user runs `ooo update`, the PyPI package and Claude Code plugin are upgraded, but the `<!-- ooo:VERSION:X.Y.Z -->` marker in project-level `CLAUDE.md` files remains on the old version. This creates version drift that must be fixed manually.

## Changes

**`skills/update/SKILL.md`** — Added step 4d:
1. Checks if `CLAUDE.md` in the current directory has an `<!-- ooo:VERSION:... -->` marker
2. If the marker version differs from the newly installed version, updates it via `sed`
3. Skips silently if no Ouroboros block is present
4. Notes that full block content regeneration requires `ooo setup`

Also updated step 5 (post-update guidance) to mention `ooo setup` for content changes.

## Test plan

- [ ] Run `ooo update` in a project with an existing CLAUDE.md Ouroboros block — verify version marker is updated
- [ ] Run `ooo update` in a project without CLAUDE.md — verify no errors
- [ ] Run `ooo update` in a project with CLAUDE.md but no Ouroboros block — verify skipped silently

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
