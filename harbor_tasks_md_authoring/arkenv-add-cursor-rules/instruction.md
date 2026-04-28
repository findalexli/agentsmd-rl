# Add cursor rules

Source: [yamcodes/arkenv#271](https://github.com/yamcodes/arkenv/pull/271)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/arktype.mdc`
- `.cursor/rules/coding-guidelines.mdc`
- `.cursor/rules/monorepo.mdc`
- `.cursor/rules/pnpm.mdc`
- `.cursor/rules/test-patterns.mdc`

## What to add / change

Closes #266 

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added comprehensive developer guides covering ArkType patterns, coding standards, monorepo structure, package management practices, and testing patterns.

* **Chores**
  * Enhanced internal development resources and configuration standards to improve consistency across the project.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
