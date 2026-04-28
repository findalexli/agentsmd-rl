# feat: add cursor testing rules

Source: [backstage/backstage#31757](https://github.com/backstage/backstage/pull/31757)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/tests/backend-test-utils.mdc`
- `.cursor/rules/tests/test-utils.mdc`

## What to add / change

## Hey, I just made a Pull Request!

<!-- Please describe what you added, and add a screenshot if possible.
     That makes it easier to understand the change so we can :shipit: faster. -->

Adds Cursor rules to enforce using `@backstage/backend-test-utils` and `@backstage/test-utils` in tests. Rules apply to files matching `**/*.test.*` and `**/*.spec.*` and provide guidance on available utilities and usage patterns. This ensures consistent test setup and reduces boilerplate by preferring standard utilities over custom mocks.

#### :heavy_check_mark: Checklist

<!--- Please include the following in your Pull Request when applicable: -->

- [ ] A changeset describing the change and affected packages. ([more info](https://github.com/backstage/backstage/blob/master/CONTRIBUTING.md#creating-changesets))
- [ ] Added or updated documentation
- [ ] Tests for new functionality and regression tests for bug fixes
- [ ] Screenshots attached (for UI changes)
- [x] All your commits have a `Signed-off-by` line in the message. ([more info](https://github.com/backstage/backstage/blob/master/CONTRIBUTING.md#developer-certificate-of-origin))

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
