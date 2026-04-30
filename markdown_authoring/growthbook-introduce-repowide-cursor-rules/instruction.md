# Introduce repo-wide Cursor rules

Source: [growthbook/growthbook#5167](https://github.com/growthbook/growthbook/pull/5167)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/backend/api-patterns.md`
- `.cursor/rules/backend/model-patterns.md`
- `.cursor/rules/development-guidelines.md`
- `.cursor/rules/frontend/data-fetching.md`
- `.cursor/rules/frontend/react-patterns.md`
- `.cursor/rules/package-boundaries.md`
- `.cursor/rules/permissions.md`
- `.cursor/rules/project-overview.md`

## What to add / change

### Features and Changes

Builds out some repo-wide Cursor rules using the `Project Rules` pattern documented by Cursor [here](https://cursor.com/docs/context/rules#project-rules).

- Closes **(add link to issue here)**

### Dependencies

<!--
Please include dependencies that must be met before deploying, if applicable. If none, you can write None or delete this section.
 -->

### Testing

<!--
  Please describe how to test these changes.
 -->

### Screenshots

<!--
  For any UI changes, e.g. changes to /front-end or docs components, please include screenshots
-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
