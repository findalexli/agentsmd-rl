# fix(pr-automation): symlink node_modules in worktree for lint/tsc/test

Source: [iOfficeAI/AionUi#1977](https://github.com/iOfficeAI/AionUi/pull/1977)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/pr-automation/SKILL.md`
- `.claude/skills/pr-fix/SKILL.md`
- `.claude/skills/pr-review/SKILL.md`

## What to add / change

## Summary

- Add `ln -s "$REPO_ROOT/node_modules" "$WORKTREE_DIR/node_modules"` after worktree creation in pr-review, pr-fix, and pr-automation skills
- `git worktree add` only includes git-tracked files, so without the symlink `bun run lint/test` and `bunx tsc` fail inside the worktree

## Test plan

- [ ] Run `/pr-review <PR>` — verify lint/tsc run without "module not found" errors in worktree
- [ ] Run `/pr-fix <PR>` — verify quality gate (lint, format, tsc, test) passes in worktree
- [ ] Trigger pr-automation rebase path — verify tsc/lint pass after rebase in worktree

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
