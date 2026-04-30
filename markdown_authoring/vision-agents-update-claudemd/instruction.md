# Update CLAUDE.md

Source: [GetStream/Vision-Agents#499](https://github.com/GetStream/Vision-Agents/pull/499)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Improve testing instructions
- Update code style rules


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Updated internal development guidelines for testing practices and code style standards to enhance code quality and consistency.

---

**Note:** This release contains no user-facing changes. Updates are limited to internal development documentation.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
