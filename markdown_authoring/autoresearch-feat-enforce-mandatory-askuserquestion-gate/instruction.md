# feat: enforce mandatory AskUserQuestion gate for all commands

Source: [uditgoenka/autoresearch#27](https://github.com/uditgoenka/autoresearch/pull/27)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/autoresearch/SKILL.md`
- `.claude/skills/autoresearch/references/debug-workflow.md`
- `.claude/skills/autoresearch/references/fix-workflow.md`
- `.claude/skills/autoresearch/references/plan-workflow.md`
- `.claude/skills/autoresearch/references/security-workflow.md`
- `.claude/skills/autoresearch/references/ship-workflow.md`

## What to add / change

## Summary

- Add **MANDATORY: Interactive Setup Gate** routing table at the top of `SKILL.md` that maps every command to its required context and `AskUserQuestion` flow
- Strengthen all interactive setup sections across 6 files with `CRITICAL`, `BLOCKING PREREQUISITE`, `MUST`, and `DO NOT skip` language
- Add **STOP guards** at Phase 1 entry points in `debug-workflow.md` and `fix-workflow.md` to catch execution without prior interactive setup

## Problem

When `/autoresearch` or any subcommand (`/autoresearch:debug`, `/autoresearch:fix`, `/autoresearch:security`, `/autoresearch:ship`, `/autoresearch:plan`) was invoked **without required context**, Claude would skip the interactive setup and proceed directly to execution phases — never calling `AskUserQuestion` to gather missing configuration from the user.

### Root Causes Identified

1. **No mandatory language** — Setup instructions used descriptive "use AskUserQuestion" instead of imperative "MUST use AskUserQuestion"
2. **No routing guard** — The Setup Phase in `SKILL.md` was buried at line 257; subcommands jumped to reference files bypassing it entirely
3. **Interactive setup buried** — In reference files, the setup section was positioned as a peer to execution phases rather than a blocking prerequisite

## Changes

| File | Change |
|------|--------|
| `SKILL.md` | Added routing table near top with required context per command; strengthened Setup Phase wording |
| `references/debug-workflow.md` | Renamed section to `PRE

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
