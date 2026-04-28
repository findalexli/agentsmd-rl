# feat(dev): add claude-compatible skills for git-pr and test-validate

Source: [4thfever/cultivation-world-simulator#96](https://github.com/4thfever/cultivation-world-simulator/pull/96)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/git-pr/SKILL.md`
- `.claude/skills/test-validate/SKILL.md`

## What to add / change

## Summary

Add two Claude/OpenCode compatible skills for this project:
- `git-pr`: SOP for creating PRs with proper remote handling
- `test-validate`: SOP for running Python tests using project venv

## Test Plan

Skills are loaded automatically by OpenCode/Claude Code from `.claude/skills/*/SKILL.md`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
