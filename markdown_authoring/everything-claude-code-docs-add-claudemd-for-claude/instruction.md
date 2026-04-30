# docs: add CLAUDE.md for Claude Code guidance

Source: [affaan-m/everything-claude-code#251](https://github.com/affaan-m/everything-claude-code/pull/251)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

- Add project-level CLAUDE.md with test commands, architecture overview, key commands, and contribution guidelines

## Test plan

- [ ] Verify CLAUDE.md is properly formatted
- [ ] Check that all test commands work

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added internal developer documentation guide with project setup, testing, and contribution information.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
