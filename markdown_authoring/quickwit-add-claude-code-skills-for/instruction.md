# Add Claude Code skills for bump-tantivy and simple-pr workflows

Source: [quickwit-oss/quickwit#6122](https://github.com/quickwit-oss/quickwit/pull/6122)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/bump-tantivy/SKILL.md`
- `.claude/skills/simple-pr/SKILL.md`

## What to add / change

Adds two Claude Code automation skills:

- **bump-tantivy**: Automates the process of bumping tantivy to the latest commit on main, fixing compilation issues, and opening a PR
- **simple-pr**: Automates creating PRs from staged changes with auto-generated commit messages

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
