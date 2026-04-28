# fix: add OKR API restriction in SKILL.md

Source: [larksuite/cli#546](https://github.com/larksuite/cli/pull/546)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/lark-okr/SKILL.md`

## What to add / change

## Summary
Add OKR domain skill reference docs and improve e2e test infrastructure for OKR shortcuts.

## Changes
- Improved API Resources descriptions

## Test Plan
- [x] Existing unit tests pass (`make unit-test`)

## Related Issues
- None

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

## Documentation
- Updated documentation for OKR cycle and objective management endpoints, specifying that positions must not overlap, weights must sum to 1.0, and all related objectives must be updated together in a single request.
- Enhanced documentation for objective alignment operations with explicit constraints preventing self-targeting and requiring overlapping time ranges between aligned objectives.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
