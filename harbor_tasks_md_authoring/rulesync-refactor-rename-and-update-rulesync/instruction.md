# refactor: rename and update rulesync skills

Source: [dyoshikawa/rulesync#1397](https://github.com/dyoshikawa/rulesync/pull/1397)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.rulesync/skills/draft-release/SKILL.md`
- `.rulesync/skills/post-review-comments/SKILL.md`
- `.rulesync/skills/release/SKILL.md`
- `.rulesync/skills/review-and-comments/SKILL.md`

## What to add / change

## Summary
- Rename `post-review-comment` skill to `post-review-comments`
- Rename `release` skill to `draft-release` and update content to match `draft-release.yml` workflow
- Add `review-and-comments` skill that runs `review-pr` then `post-review-comments` sequentially

## Test plan
- [ ] Verify `pnpm dev generate` works correctly with renamed skills
- [ ] Verify each skill is recognized by name in the generated output

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
