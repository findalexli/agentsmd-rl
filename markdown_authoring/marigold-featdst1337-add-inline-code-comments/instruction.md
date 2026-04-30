# feat(DST-1337): add inline code comments option to review-pr skill

Source: [marigold-ui/marigold#5325](https://github.com/marigold-ui/marigold/pull/5325)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/review-pr/SKILL.md`
- `.claude/skills/review-pr/references/review-checklist.md`

## What to add / change

## Summary
- Adds inline code comments as a posting option in the `review-pr` skill
- The skill now offers 4 options after generating a review: **inline comments**, **full PR comment**, **both**, or **skip**
- Inline comments use `gh api` to place feedback directly on the relevant code lines in the diff, with severity emoji prefixes and GitHub suggestion blocks
- **New:** Automatically checks whether visual regression tests (Chromatic) should run for the branch
  - Detects UI-affecting file changes (`packages/components/src/**`, `themes/**`, `*.stories.tsx`, etc.)
  - Queries the `Visual-Regression-Tests` workflow via `gh run list` and compares the run's `headSha` against the current PR head
  - Posts a resolvable inline comment when VRT is needed but **not started**, **stale** (new commits since last run), or **failed**
  - Skips the comment when VRT is already running or passed on the current head


🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
