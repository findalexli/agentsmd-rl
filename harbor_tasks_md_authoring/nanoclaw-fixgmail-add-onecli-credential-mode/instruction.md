# fix(gmail): add OneCLI credential mode detection

Source: [qwibitai/nanoclaw#1660](https://github.com/qwibitai/nanoclaw/pull/1660)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-gmail/SKILL.md`

## What to add / change

<!-- contributing-guide: v1 -->
## Type of Change

- [x] **Feature skill** - adds a channel or integration (source code changes + SKILL.md)
- [ ] **Utility skill** - adds a standalone tool (code files in `.claude/skills/<name>/`, no source changes)
- [ ] **Operational/container skill** - adds a workflow or agent skill (SKILL.md only, no source changes)
- [ ] **Fix** - bug fix or security fix to source code
- [ ] **Simplification** - reduces or simplifies source code
- [ ] **Documentation** - docs, README, or CONTRIBUTING changes only

## Description

Updates the Gmail skill setup flow to auto-detect credential mode.
If OneCLI is configured, guides users through `onecli apps connect`.
Otherwise falls back to manual GCP OAuth (existing flow).

## For Skills

- [x] SKILL.md contains instructions, not inline code (code goes in separate files)
- [x] SKILL.md is under 500 lines
- [ ] I tested this skill on a fresh clone

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
