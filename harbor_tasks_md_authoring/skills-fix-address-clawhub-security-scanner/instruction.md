# fix: address ClawHub security scanner flags

Source: [heygen-com/skills#40](https://github.com/heygen-com/skills/pull/40)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `heygen-video/SKILL.md`
- `platforms/nanoclaw/heygen/SKILL.md`

## What to add / change

Fixes all four issues flagged by the ClawHub security scan on heygen-skills.

**Fix 1: Remove update-check.sh autorun**
The preamble previously ran `scripts/update-check.sh` automatically on every skill invocation. Removed. Script is now opt-in only with explicit docs.

**Fix 2: Safe config file read**
Replaced `source ~/.heygen/config` (arbitrary shell code execution risk) with a safe `grep/cut` read that only extracts the `HEYGEN_API_KEY` value.

**Fix 3: Clarify auto_proceed intent**
Added explicit documentation that `auto_proceed: true` is required API behavior — HeyGen Video Agent pauses at a review checkpoint by default, causing videos to never complete without it. Not a security bypass.

**Fix 4: Fix v2 endpoints in nanoclaw SKILL.md**
Updated `/v2/avatars` and `/v2/voices` to `/v3/avatars` and `/v3/voices` with correct response field paths.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
