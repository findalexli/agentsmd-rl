# Simplify agent rule entrypoints

Source: [study8677/antigravity-workspace-template#50](https://github.com/study8677/antigravity-workspace-template/pull/50)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `cli/src/ag_cli/templates/AGENTS.md`

## What to add / change

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Simplified and updated internal developer guidance documentation with streamlined engineering principles and best practices.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
