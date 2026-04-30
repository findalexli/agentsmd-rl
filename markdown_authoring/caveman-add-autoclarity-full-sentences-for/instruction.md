# Add Auto-Clarity: full sentences for security warnings and destructive ops

Source: [JuliusBrussee/caveman#12](https://github.com/JuliusBrussee/caveman/pull/12)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/caveman/SKILL.md`

## What to add / change

## What

Adds an **Auto-Clarity** section to `SKILL.md`. Caveman drops compressed grammar and uses full sentences for responses where fragmentation risks misunderstanding or harm — then resumes caveman immediately after.

## Why

Current `Boundaries` section covers code blocks and git commits but leaves a gap: destructive confirmations, security warnings, and multi-step sequences where fragment order matters. A caveman response like `Delete all users. Run: DROP TABLE users;` skips the warning that should precede it.

## When Auto-Clarity triggers

- Security warning or destructive action confirmation (delete, drop, force-push)
- Irreversible action — data loss possible
- Multi-step sequence where fragment order risks misread
- Error diagnosis needing precise cause → effect chain
- User explicitly confused or asking for clarification

## Before / After

**Before** (caveman, no guard):
> Delete all users. Run: `DROP TABLE users;`

**After** (auto-clarity kicks in):
> **Warning:** This will permanently delete all rows in the `users` table and cannot be undone. To proceed, run:
> ```sql
> DROP TABLE users;
> ```
> Caveman resume. Verify backup exist first.

---
Orthogonal to PR #11 (intensity levels). No conflict.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
