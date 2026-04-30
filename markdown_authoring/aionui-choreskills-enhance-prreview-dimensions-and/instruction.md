# chore(skills): enhance pr-review dimensions and pr-fix worktree setup

Source: [iOfficeAI/AionUi#2064](https://github.com/iOfficeAI/AionUi/pull/2064)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/pr-fix/SKILL.md`
- `.claude/skills/pr-review/SKILL.md`

## What to add / change

## Summary

- Add `electron-rebuild` step to pr-fix skill worktree setup, ensuring native modules (e.g., `better-sqlite3`) are ABI-compatible with Electron
- Add three new review dimensions to pr-review skill: database migration correctness, IPC bridge / preload security, and Electron security configuration
- All new dimensions flag regressions as CRITICAL severity

## Test plan

- [ ] Verify pr-fix skill correctly runs electron-rebuild in worktree
- [ ] Verify pr-review skill evaluates the new dimensions on relevant PRs

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
