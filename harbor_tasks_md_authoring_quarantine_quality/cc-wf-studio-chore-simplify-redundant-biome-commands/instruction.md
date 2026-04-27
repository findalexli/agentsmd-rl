# chore: simplify redundant Biome commands in CLAUDE.md

Source: [breaking-brake/cc-wf-studio#711](https://github.com/breaking-brake/cc-wf-studio/pull/711)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Simplify code quality check instructions by replacing redundant triple-command chain with a single `npm run check`.

## What Changed

### Before
- CLAUDE.md instructed running `npm run format && npm run lint && npm run check` (3 commands)
- `format` and `lint` are already included in `check`, making the first two redundant

### After
- Single `npm run check` command covers lint + format with auto-fix

## Changes

- `CLAUDE.md` - Replaced 3 occurrences of redundant command chains with `npm run check`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Updated development documentation to reflect a streamlined code quality verification process using a consolidated command.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
