# feat: add Angular project cursor rules and guidelines for best practices

Source: [ng-select/ng-select#2699](https://github.com/ng-select/ng-select/pull/2699)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/rules.mdc`

## What to add / change

- Introduced a comprehensive set of rules for Angular projects, covering topics such as using the latest Angular and TypeScript versions, modern features, component architecture, type safety, dependency injection, API communication, state management, testing, accessibility, and documentation.
- Emphasized the use of Angular signals, standalone components, and strict typing to enhance code quality and maintainability.
- Included guidelines for code generation to ensure consistency and adherence to best practices.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
