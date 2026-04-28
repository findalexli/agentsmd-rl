# feat: add spec-interview skill for requirement gathering

Source: [4thfever/cultivation-world-simulator#103](https://github.com/4thfever/cultivation-world-simulator/pull/103)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/spec-interview/SKILL.md`

## What to add / change

## Summary

Adds a new `/spec-interview` skill that conducts in-depth interviews using `AskUserQuestion` to gather requirements before writing specification documents.

Key features:
- Adaptive questioning based on topic complexity (not a rigid checklist)
- Focuses on non-obvious questions: hidden assumptions, edge cases, tradeoffs, failure modes
- Knows when to stop — not every topic needs exhaustive coverage
- Outputs specs to `docs/specs/<feature-name>.md`

## Test Plan

- [x] Verified skill file is correctly formatted with YAML frontmatter
- [x] Tested `/spec-interview` invocation locally

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
