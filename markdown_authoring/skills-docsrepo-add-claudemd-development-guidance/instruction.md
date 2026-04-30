# docs(repo): add CLAUDE.md development guidance

Source: [posit-dev/skills#31](https://github.com/posit-dev/skills/pull/31)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Adds CLAUDE.md with comprehensive guidance for Claude Code when working in this skills repository. Includes repository structure, SKILL.md format, skill registration process, and key development conventions.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
