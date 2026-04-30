# feat(conventional-git): add worktree naming conventions

Source: [samber/cc-skills#12](https://github.com/samber/cc-skills/pull/12)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/conventional-git/SKILL.md`

## What to add / change

## Summary

- Add **Worktree Naming** section: directory name mirrors the branch name (`/` → `-`), always placed under `.claude/worktrees/`
- Document worktree cleanup after merge: `git worktree remove` + `git worktree prune`
- Update `description` frontmatter to trigger on worktree naming requests
- Bump skill to v1.2.0

## Test plan

- [ ] `git worktree add .claude/worktrees/feat-foo feat/foo` pattern is followed
- [ ] Cleanup commands (`worktree remove`, `worktree prune`) are present
- [ ] Description mentions worktree naming as a trigger

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
