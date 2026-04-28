# feat: add git-worktree-runner (gtr) skill

Source: [dyoshikawa/rulesync#1178](https://github.com/dyoshikawa/rulesync/pull/1178)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.rulesync/skills/git-worktree-runner/SKILL.md`

## What to add / change

## Summary
- Add a new skill for git-worktree-runner (gtr), a CLI tool that wraps `git worktree` with editor and AI tool integration
- Includes command reference (create, list, remove, navigate worktrees), configuration guide, and practical examples (parallel AI development, PR review, hotfix workflows)

## Test plan
- [ ] Verify `pnpm dev generate` produces correct output for the new skill
- [ ] Confirm skill is recognized by Claude Code after generation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
