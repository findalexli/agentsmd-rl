# Create SKILL.md for Manifest skill

Source: [mnfst/manifest#736](https://github.com/mnfst/manifest/pull/736)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/manifest/SKILL.md`

## What to add / change

Add placeholder content for the Manifest skill.

## Summary

<!-- Briefly describe what this PR does and why -->

## Changes

## <!-- List the main changes made in this PR -->

## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactoring (no functional changes)
- [ ] Documentation update
- [ ] Tests (adding or updating tests)
- [ ] CI/CD (changes to build process or workflows)

## Testing

<!-- Describe how you tested your changes -->

- [ ] Tests pass locally (`pnpm test`)
- [ ] Lint passes (`pnpm lint`)

## Related Issues

<!-- Link any related issues: Fixes #123, Relates to #456 -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
