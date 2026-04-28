# docs: add test coverage guidelines to test-validate skill

Source: [4thfever/cultivation-world-simulator#99](https://github.com/4thfever/cultivation-world-simulator/pull/99)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/test-validate/SKILL.md`

## What to add / change

## Summary

Add test coverage guidelines to the `test-validate` skill to help developers decide when tests are needed.

| Change Type | Test Recommendation |
|-------------|---------------------|
| Bug fix | Add regression test to prevent recurrence |
| New feature | Unit tests + integration test if affects multiple modules |
| Refactor | Existing tests should pass; add tests if behavior changes |
| Config/docs | Usually no tests needed |

## Test Plan

- [x] Documentation only, no code changes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
