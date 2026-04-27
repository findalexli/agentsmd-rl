# fix(skills): fetch base branch before three-dot diff to prevent stale ref

Source: [iOfficeAI/AionUi#2097](https://github.com/iOfficeAI/AionUi/pull/2097)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/pr-automation/SKILL.md`
- `.claude/skills/pr-review/SKILL.md`

## What to add / change

## Summary

- pr-review and pr-automation skills only fetched PR head (`git fetch origin pull/N/head`) but never updated the base branch ref, causing `git diff origin/<base>...HEAD` to include changes from other already-merged PRs when the local `origin/main` was stale
- Added `git fetch origin <base_branch>` before every three-dot diff and rebase operation across both skills (5 locations total)
- Root cause of PR #2096 review containing unrelated agent disconnect changes despite the PR only modifying 2 theme color files

## Test plan

- [ ] Run `pr-review` on a small PR and verify the diff matches the actual PR files
- [ ] Run `pr-automation` full cycle and confirm review accuracy
- [ ] Verify pr-fix worktree rebase uses fresh base branch

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
