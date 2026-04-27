# fix: scope commit-push-pr descriptions to full branch diff

Source: [EveryInc/compound-engineering-plugin#385](https://github.com/EveryInc/compound-engineering-plugin/pull/385)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md`

## What to add / change

The `git-commit-push-pr` skill wrote PR descriptions from `git diff HEAD` (uncommitted changes only), so when a branch had prior commits the description silently ignored them — covering only whatever happened to be uncommitted at invocation time.

Adds a base-branch and remote detection step before the PR description is written. The detection uses the same fallback chain as `ce-review`: PR `baseRefName` + base-repo remote resolution, `origin/HEAD`, GitHub default-branch metadata, then common branch names (`main`, `master`, `develop`, `trunk`). This handles fork-based PRs where the base lives on a remote other than `origin`, and repos whose default branch isn't `main`.

The full branch diff (`git diff <merge-base>...HEAD`) and commit list (`git log <merge-base>..HEAD`) now drive the PR description instead of the working-tree diff.

---

[![Compound Engineering v2.53.0](https://img.shields.io/badge/Compound_Engineering-v2.53.0-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
🤖 Generated with Claude Opus 4.6 (1M context) via Claude Code

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
