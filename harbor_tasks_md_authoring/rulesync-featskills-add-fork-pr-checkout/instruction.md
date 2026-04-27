# feat(skills): add fork PR checkout workflow to git-worktree-runner skill

Source: [dyoshikawa/rulesync#1233](https://github.com/dyoshikawa/rulesync/pull/1233)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.rulesync/skills/git-worktree-runner/SKILL.md`

## What to add / change

## Summary
- Add documentation for checking out GitHub PRs from forked repositories into git worktrees
- Uses GitHub's `refs/pull/<number>/head` ref to fetch fork PR branches via `origin`
- Includes step-by-step procedure, full examples, branch name shortening tips, and common error handling

## Test plan
- [x] `pnpm cicheck` passes
- [ ] Verify the skill is loaded correctly in Claude Code sessions

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
