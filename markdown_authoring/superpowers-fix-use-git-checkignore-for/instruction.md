# fix: use git check-ignore for worktree gitignore verification

Source: [obra/superpowers#160](https://github.com/obra/superpowers/pull/160)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/using-git-worktrees/SKILL.md`

## What to add / change

## Summary

Fixes #101

The `using-git-worktrees` skill previously used `grep` to check only the local `.gitignore` file, missing patterns in global gitignore configurations (`core.excludesfile`). This caused unnecessary modifications to local `.gitignore` when the directory was already globally ignored.

Changed verification from `grep` to `git check-ignore`, which respects Git's full ignore hierarchy (local, global, and system gitignore files).

## Changes

- Safety Verification command: `grep` → `git check-ignore -q`
- Updated Quick Reference table, Common Mistakes, Example Workflow, Red Flags, and Always sections for consistency

## Testing

Followed TDD process per the writing-skills skill:
- **RED:** Baseline test with subagent showed agent would incorrectly conclude directory NOT ignored when using global gitignore, then unnecessarily modify local `.gitignore`
- **GREEN:** After fix, agent correctly uses `git check-ignore` and recognizes globally-ignored directories
- **REFACTOR:** Verified fix works correctly - agent no longer attempts to modify `.gitignore` when directory is already globally ignored

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Updated Git worktrees guide to emphasize verifying that directories are ignored (rather than merely listed in .gitignore) before creating worktrees.
  * Guidance and examples now recom

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
