# docs: Add testing guidance to CLAUDE.md

Source: [liam-hq/liam#3749](https://github.com/liam-hq/liam/pull/3749)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Issue

- resolve: (none - documentation improvement)

## Why is this change needed?

Add reference to test-principles.md in CLAUDE.md to ensure Claude Code follows established testing principles when writing tests.

## Summary

- Added Testing section to CLAUDE.md that references @docs/test-principles.md

## Test plan

- [ ] Verify CLAUDE.md renders correctly
- [ ] Confirm @docs/test-principles.md reference works in Claude Code

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

- Documentation
  - Expanded CSS/Testing guidance with a new Testing subsection that references established test principles for consistency.
  - Clarifies expectations for testing approaches without altering application behavior.
  - No functional, UI, or performance changes; user experience remains unchanged.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
