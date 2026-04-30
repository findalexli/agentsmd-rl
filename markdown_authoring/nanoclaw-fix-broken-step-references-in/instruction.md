# fix broken step references in setup/SKILL.md

Source: [qwibitai/nanoclaw#794](https://github.com/qwibitai/nanoclaw/pull/794)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/setup/SKILL.md`

## What to add / change

## Type of Change

- [ ] **Skill** - adds a new skill in `.claude/skills/`
- [x] **Fix** - bug fix or security fix to source code
- [ ] **Simplification** - reduces or simplifies source code

## Description

Corrected multiple references pointing to non-existent steps 4c,
updating them to correctly point to step 3c (Build and test).

## For Skills

- [x] I have not made any changes to source code
- [x] My skill contains instructions for Claude to follow (not pre-built code)
- [x] I tested this skill on a fresh clone

## Changes

- In Step 3a (Choose runtime): Updated the Apple Container path to skip to `3c` instead of `4c`.
- In Step 3b (Apple Container conversion gate): Updated both the "Already converted" and "Docker" paths to continue to `3c` instead of `4c`.

## Related Issue
Fixes #793

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
