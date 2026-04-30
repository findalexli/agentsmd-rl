# feat(skills): add search-first skill

Source: [affaan-m/everything-claude-code#262](https://github.com/affaan-m/everything-claude-code/pull/262)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/search-first/SKILL.md`

## What to add / change

> **Re-submission of #258** (closed due to broken fork relationship)

## Summary

Adds a `search-first` skill that enforces a research-before-coding workflow: search for existing tools, libraries, and patterns before writing custom code.

## Test plan

- [ ] Verify YAML frontmatter is valid
- [ ] Confirm `description` starts with "Use when..."

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
