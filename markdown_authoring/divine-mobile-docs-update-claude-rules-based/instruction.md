# docs: update Claude rules based on PR feedback

Source: [divinevideo/divine-mobile#3018](https://github.com/divinevideo/divine-mobile/pull/3018)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/architecture.md`
- `.claude/rules/code_style.md`
- `.claude/rules/state_management.md`
- `.claude/rules/testing.md`

## What to add / change

Closes #3019

## Description

Update Claude rules based on recurring PR feedback patterns. Adds new guidance for package extraction triggers, test coverage expectations for new packages, dependency version freshness, PR scope discipline, temporary code documentation, and when to use stored state vs getters for expensive computations.

## Type of Change

- [ ] New feature (non-breaking change which adds functionality)
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Code refactor
- [ ] Build configuration change
- [x] Documentation
- [ ] Chore

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
