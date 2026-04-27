# Add Code Review skill

Source: [openai/codex#18746](https://github.com/openai/codex/pull/18746)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.codex/skills/code-review-breaking-changes/SKILL.md`
- `.codex/skills/code-review-change-size/SKILL.md`
- `.codex/skills/code-review-context/SKILL.md`
- `.codex/skills/code-review-testing/SKILL.md`
- `.codex/skills/code-review/SKILL.md`

## What to add / change

Adds a skill that centralizes rules used during code review for codex.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
