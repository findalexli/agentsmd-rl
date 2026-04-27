# feat(ce-work): suggest branch rename when worktree name is meaningless

Source: [EveryInc/compound-engineering-plugin#451](https://github.com/EveryInc/compound-engineering-plugin/pull/451)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-work-beta/SKILL.md`
- `plugins/compound-engineering/skills/ce-work/SKILL.md`

## What to add / change

## Summary

When `ce:work` starts on a worktree with an auto-generated branch name like `worktree-jolly-beaming-raven` (commonplace with claude code auto generated worktree names), it currently offers to "Continue here (Recommended)" without noticing the name carries no context. Reviewers, git log readers, and the user themselves get nothing useful from the branch name.

This adds a meaningful-name check to the "already on a feature branch" path in both `ce:work` and `ce:work-beta`. When the branch name appears auto-generated or opaque, the skill now suggests `git branch -m` to a name derived from the plan or work description before continuing — while still allowing the user to keep the current name if they prefer.

## Test plan

- Start `ce:work` while on a `worktree-*` branch — verify the skill suggests a rename
- Start `ce:work` while on a `feat/something-meaningful` branch — verify no rename suggestion, behavior unchanged

---

[![Compound Engineering v2.59.0](https://img.shields.io/badge/Compound_Engineering-v2.59.0-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
🤖 Generated with Claude Opus 4.6 (1M context, extended thinking) via [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
