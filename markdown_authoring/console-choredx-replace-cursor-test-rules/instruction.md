# chore(dx): replace cursor test rules with claude testing skill

Source: [akash-network/console#2912](https://github.com/akash-network/console/pull/2912)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/console-tests/SKILL.md`
- `.claude/skills/console-tests/references/api-patterns.md`
- `.claude/skills/console-tests/references/frontend-patterns.md`
- `.cursor/rules/no-jest-mock.mdc`
- `.cursor/rules/query-by-in-tests.mdc`
- `.cursor/rules/setup-instead-of-before-each.mdc`
- `.cursor/rules/test-descriptions.mdc`

## What to add / change

## Why

The 4 test-related cursor rules (no-jest-mock, query-by-in-tests, setup-instead-of-before-each, test-descriptions) are scattered and limited in scope. This consolidates them into a single comprehensive Claude skill that covers all testing conventions for the monorepo.

## What

- Removes 4 cursor rule files (`.cursor/rules/no-jest-mock.mdc`, `query-by-in-tests.mdc`, `setup-instead-of-before-each.mdc`, `test-descriptions.mdc`)
- Adds `.claude/skills/console-tests/` with:
  - `SKILL.md` — main skill covering test level selection, universal rules (setup pattern, describe naming, mocking, AAA, assertions), and per-app guidance
  - `references/frontend-patterns.md` — DEPENDENCIES/COMPONENTS pattern, MockComponents, hook testing, query testing, container testing
  - `references/api-patterns.md` — unit test pattern, config mocking, seeders, functional test setup, integration tests, NestJS patterns
- `general.mdc` is intentionally kept — will be cleaned up separately

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added comprehensive testing guidance covering console, API, and frontend testing patterns: test types, setup conventions, mocking strategies, seeding, assertion practices, DI/testing utilities, and file/organization recommendations.
* **Chores**
  * Removed several legacy test-guideline documents and consolidated their guidance into the new centralized testing documentation.
<!-- end of au

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
