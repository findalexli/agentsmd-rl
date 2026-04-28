# Fix SKILL.md frontmatter to use valid properties

Source: [hardikpandya/stop-slop#3](https://github.com/hardikpandya/stop-slop/pull/3)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary
- Moves `trigger` and `author` properties under `metadata` in SKILL.md frontmatter
- Resolves the "unexpected key in SKILL.md frontmatter" error on Windows Claude Desktop

## Details
The Claude Desktop app only allows specific frontmatter properties: `name`, `description`, `license`, `allowed-tools`, `compatibility`, and `metadata`. Custom properties like `trigger` and `author` need to be nested under `metadata`.

Fixes #2

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
