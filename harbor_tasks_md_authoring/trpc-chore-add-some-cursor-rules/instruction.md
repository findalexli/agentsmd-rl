# chore: add some cursor rules

Source: [trpc/trpc#6929](https://github.com/trpc/trpc/pull/6929)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/coding-guidelines.mdc`
- `.cursor/rules/react-query-tests.mdc`
- `.cursor/rules/tanstack-react-query-tests.mdc`
- `.cursor/rules/test-patterns.mdc`
- `.cursor/rules/upgrade-tests.mdc`

## What to add / change

vibe coded them, anyone is free to change them

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Added comprehensive TypeScript coding style guidelines for tRPC to promote consistency and type safety.
  * Introduced standardized testing patterns for legacy React Query.
  * Documented testing patterns for TanStack React Query, including provider setup and utilities.
  * Established best practices for server–client test setup, resource management, and mocks.
  * Added upgrade-testing guidance covering dual-provider workflows to aid migration.
  * Overall, improves clarity, consistency, and reliability across development and testing workflows.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
