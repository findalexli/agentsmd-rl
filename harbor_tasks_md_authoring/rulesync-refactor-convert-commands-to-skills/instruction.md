# refactor: convert commands to skills format

Source: [dyoshikawa/rulesync#1391](https://github.com/dyoshikawa/rulesync/pull/1391)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.rulesync/skills/clean-worktrees/SKILL.md`
- `.rulesync/skills/create-issue/SKILL.md`
- `.rulesync/skills/explain-pr/SKILL.md`
- `.rulesync/skills/merge-pr/SKILL.md`
- `.rulesync/skills/post-review-comment/SKILL.md`
- `.rulesync/skills/release-dry-run/SKILL.md`
- `.rulesync/skills/release/SKILL.md`
- `.rulesync/skills/security-scan-diff/SKILL.md`

## What to add / change

## Summary
- Convert 7 command files from `.rulesync/commands/` to skill format (`.rulesync/skills/<name>/SKILL.md`)
- Converted: clean-worktrees, create-issue, explain-pr, merge-pr, post-review-comment, release-dry-run, release, security-scan-diff
- Only `draft-release-post.md` remains as a command

## Test plan
- [x] `pnpm cicheck` passes
- [x] Pre-commit hooks pass
- [ ] Verify skills are correctly recognized by rulesync generation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
