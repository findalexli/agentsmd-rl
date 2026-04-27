# docs: add reference routing to skills for discoverabilityFix/add reference routing

Source: [addyosmani/agent-skills#34](https://github.com/addyosmani/agent-skills/pull/34)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/code-review-and-quality/SKILL.md`
- `skills/frontend-ui-engineering/SKILL.md`
- `skills/performance-optimization/SKILL.md`
- `skills/security-and-hardening/SKILL.md`
- `skills/shipping-and-launch/SKILL.md`
- `skills/test-driven-development/SKILL.md`

## What to add / change

## Summary

Adds "See Also" sections to 6 skills, routing agents to the 4 reference checklists during execution. Fixes #26.

## Changes

- `security-and-hardening`: Link to security-checklist
- `code-review-and-quality`: Link to security-checklist and performance-checklist
- `shipping-and-launch`: Link to all 3 checklists
- `performance-optimization`: Link to performance-checklist
- `frontend-ui-engineering`: Link to accessibility-checklist
- `test-driven-development`: Link to testing-patterns

## Verification

- [x] All 6 skill files updated
- [x] No breaking changes to existing sections
- [x] Links reference correct file paths
- [x] "See Also" sections placed consistently (before "Common Rationalizations")

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
