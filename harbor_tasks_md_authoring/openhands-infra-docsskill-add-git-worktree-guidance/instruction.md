# docs(skill): add git worktree guidance to github-workflow skill

Source: [zxkane/openhands-infra#33](https://github.com/zxkane/openhands-infra/pull/33)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/github-workflow/SKILL.md`

## What to add / change

## Summary

Add git worktree usage guidance to the `github-workflow` skill based on practical experience from the git-changes-500 fix (PR #32).

### Changes

- Updated Step 1 in the workflow overview to mention worktrees as the preferred approach for isolated development
- Added a dedicated "Git Worktree Usage" section covering:
  - When to use worktrees vs. simple branch checkout (decision table)
  - Step-by-step: create, work, copy local files, cleanup
  - Handling of gitignored files (deploy scripts, `CLAUDE.local.md`)
  - Python venv path note (shared `.venv/` lives in main repo)
  - Quick reference commands

## Test plan

- [x] Docs-only change — no build/test impact
- [ ] CI checks pass

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
