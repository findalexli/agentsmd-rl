# skill: add /update-nanoclaw

Source: [qwibitai/nanoclaw#217](https://github.com/qwibitai/nanoclaw/pull/217)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/update-nanoclaw/SKILL.md`

## What to add / change

Fixes #181 

Users with customized installs currently have no efficient way to sync upstream fixes. One user reported spending \$15 in API credits(in the discord channel) trying to merge changes manually because Claude scans the full repo and refactors unrelated code during the process.

This skill gives Claude a strict, low-token playbook: preview changes with `git log`/`git diff`, only open files with actual conflicts, never refactor surrounding code. Merge-first by default (one-pass conflict resolution instead of per-commit with rebase). Supports cherry-pick for pulling individual fixes, and abort for just viewing the changelog.

## Type of Change

- [x] **Skill** - adds a new skill in `.claude/skills/`
- [ ] **Fix** - bug fix or security fix to source code
- [ ] **Simplification** - reduces or simplifies source code

## Description

Adds `/update-nanoclaw` skill. Previews upstream changelog categorized by file type (skills/source/config), runs a dry-run conflict check, lets the user choose merge/cherry-pick/rebase/abort, resolves only conflicted files, validates with build + test. Creates timestamped backup branch + tag for rollback.

## For Skills

- [x] I have not made any changes to source code
- [x] My skill contains instructions for Claude to follow (not pre-built code)
- [x] I tested this skill on a fresh clone

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
