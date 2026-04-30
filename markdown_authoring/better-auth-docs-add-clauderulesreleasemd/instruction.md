# docs: add `.claude/rules/release.md`

Source: [better-auth/better-auth#7403](https://github.com/better-auth/better-auth/pull/7403)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/release.md`
- `CLAUDE.md`

## What to add / change

Closes: https://github.com/better-auth/better-auth/pull/7027

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Add .claude/rules/release.md documenting the release process for stable (main), beta (canary), and version-branch releases. Includes step-by-step branch flow, cherry-picking, version bump/tagging, npm tag rules, and CI requirements to prevent release mistakes.

<sup>Written for commit e5af17e35ca10152185acb50214012e86263bbea. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
