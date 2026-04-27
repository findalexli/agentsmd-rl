# fix: add default-branch guard to commit skills

Source: [EveryInc/compound-engineering-plugin#386](https://github.com/EveryInc/compound-engineering-plugin/pull/386)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md`
- `plugins/compound-engineering/skills/git-commit/SKILL.md`

## What to add / change

Both git-commit and git-commit-push-pr skills had a gap: they referenced "the repo's default branch" in their branch-protection guards but never resolved the actual default branch name. Repos using `develop`, `trunk`, or other non-standard defaults would silently bypass the guard.

Adds `git rev-parse --abbrev-ref origin/HEAD | sed 's@^origin/@@'` to Step 1 of both skills so the guard checks the real default branch, falling back to `main` if the remote HEAD is unset. Also inlines `sed` in git-commit-push-pr's Step 6 `symbolic-ref` fallback to remove a prose "strip the prefix" instruction.

---

[![Compound Engineering v2.53.0](https://img.shields.io/badge/Compound_Engineering-v2.53.0-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
🤖 Generated with Claude Opus 4.6 (1M context, extended thinking) via [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
