# chore: add to skill triager and PR reviewer instructions for by-design implementations

Source: [medusajs/medusa#15158](https://github.com/medusajs/medusa/pull/15158)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/reviewing-prs/SKILL.md`
- `.claude/skills/reviewing-prs/reference/comment-guidelines.md`
- `.claude/skills/triaging-issues/SKILL.md`
- `.claude/skills/triaging-issues/reference/bug-report.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
