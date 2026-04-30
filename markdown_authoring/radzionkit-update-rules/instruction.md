# Update rules

Source: [radzionc/radzionkit#14](https://github.com/radzionc/radzionkit/pull/14)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/add-library.mdc`
- `.cursor/rules/assert.mdc`
- `.cursor/rules/attempt-over-try-catch.mdc`
- `.cursor/rules/cusor-rules.mdc`
- `.cursor/rules/default-rule-scoping.mdc`
- `.cursor/rules/eslint-autofix.mdc`
- `.cursor/rules/functions.mdc`
- `.cursor/rules/imports.mdc`
- `.cursor/rules/package-manager.mdc`
- `.cursor/rules/readable-code-over-comments.mdc`
- `.cursor/rules/resolver-pattern.mdc`
- `.cursor/rules/trust-types-no-fallbacks.mdc`
- `.cursor/rules/typecheck-guidance.mdc`

## What to add / change

- Deleted obsolete rules including `add-library.mdc`, `cusor-rules.mdc`, and `default-rule-scoping.mdc`.
- Introduced new rules for ESLint autofix, readable code over comments, resolver patterns, and trust TypeScript values.
- Updated existing rules to enhance clarity and maintainability, ensuring alignment with current best practices in TypeScript development.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
