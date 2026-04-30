# docs: add CLAUDE.md with release process docs

Source: [saffron-health/libretto#199](https://github.com/saffron-health/libretto/pull/199)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Adds CLAUDE.md documenting the release process (`scripts/prepare-release.sh`) and mirror system
- Prevents future manual version bumps that skip SKILL.md and mirror updates

## Test plan
- N/A — documentation only

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
