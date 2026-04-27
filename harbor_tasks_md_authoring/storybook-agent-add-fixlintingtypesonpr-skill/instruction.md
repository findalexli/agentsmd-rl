# Agent: Add fix-linting-types-on-pr skill

Source: [storybookjs/storybook#34240](https://github.com/storybookjs/storybook/pull/34240)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/fix-linting-types-on-pr/SKILL.md`

## What to add / change

Closes #

<!-- If your PR is related to an issue, provide the number(s) above; if it resolves multiple issues, be sure to break them up (e.g. "closes #1000, closes #1001"). -->

<!--

Thank you for contributing to Storybook! Please submit all PRs to the `next` branch unless they are specific to the current release. Storybook maintainers cherry-pick bug and documentation fixes into the `main` branch as part of the release process, so you shouldn't need to worry about this. For additional guidance: https://storybook.js.org/docs/contribute

-->

## What I did

I've added a new skill to automatically check out PRs and fix linting and TypeScript issues.

## Checklist for Contributors

### Testing

<!-- Please check (put an "x" inside the "[ ]") the applicable items below to communicate how to test your changes -->

#### The changes in this PR are covered in the following automated tests:

- [ ] stories
- [ ] unit tests
- [ ] integration tests
- [ ] end-to-end tests

#### Manual testing

> [!CAUTION]
> This section is mandatory for all contributions. If you believe no manual test is necessary, please state so explicitly. Thanks!

<!-- Please include the steps to test your changes here. For example:

1. Run a sandbox for template, e.g. `yarn task --task sandbox --start-from auto --template react-vite/default-ts`
2. Open Storybook in your browser
3. Access X story

-->

### Documentation

<!-- Please check (put an "x" inside the "[ ]") the ap

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
